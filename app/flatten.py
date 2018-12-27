#!/usr/bin/env python

"""
Flattens Maps for Terraform to process
"""
from __future__ import print_function
from fastjsonschema import validate
import argparse
import os
import json
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def _parse_argument():
    """ parse commandline input """
    parser = argparse.ArgumentParser(description='Flattens maps for terraform to processs')
    parser.add_argument(
        '--verbose',
        '-v',
        action='count',
        help='Log verbosity')
    subparsers = parser.add_subparsers(help='sub-command help')

    # Sub command that handles IAM validation and output
    iam_parser = subparsers.add_parser('iam',
        description='Flattens IAM Json Object passed down by Terraform',
        help='Flattens IAM Json Encoded Object passed down by Terraform')
    iam_parser.add_argument(
        'json',
        type=str,
        help='Json Encoded IAM Object'
    )
    iam_parser.set_defaults(func=iam)

    # Sub command that handles Firewall validation and output
    fw_parser = subparsers.add_parser('fw',
        description='Flattens FW Json Object passed down by Terraform',
        help='Flattens FW Json Encoded Object passed down by Terraform')
    fw_parser.add_argument(
        '--ingress',
        action='store_true',
        help='Wether json passed is for ingress. Assumes its egress if flag not passed.'
    )
    fw_parser.add_argument(
        'json',
        type=str,
        help='Json Encoded IAM Object'
    )
    fw_parser.set_defaults(func=firewall)

    return parser.parse_args()

def iam(args):
    # retrieving relative path for schema.json
    dirname = os.path.dirname(__file__)
    schema_path = os.path.join(dirname, 'schema/iam.json')

    # loading schema as JSON Object
    with open(schema_path) as f:
        schema = json.load(f)
    data = json.loads(args.json)

    # Validating input against schema
    validate(schema, data)

    # building flat map. 
    # Keys are seperated via | 
    # Emails are seperated via space
    # Roles are seperated via ,
    output = ""
    for k in data:
        output = output + k + "|"
        for access in data[k]:
            output = output + access + " "
        output = output + ","
    # result is stored into a json object
    json_obj = { "iam": output }
    # results are dumped to stdout 
    print(json.dumps(json_obj, indent=4))

def firewall(args):
    # retrieving relative path for schema.json
    dirname = os.path.dirname(__file__)
    if args.ingress:
        schema_path = os.path.join(dirname, 'schema/fw-ingress.json')
    else:
        schema_path = os.path.join(dirname, 'schema/fw-egress.json')

    # loading schema as JSON Object
    with open(schema_path) as f:
        schema = json.load(f)
    data = json.loads(args.json)

    # Validating input against schema
    validate(schema, data)

    allow_output = assembleIngressFWString(data, "allow") if args.ingress else assembleEgressFWString(data, "allow")
    deny_output = assembleIngressFWString(data, "deny") if args.ingress else assembleEgressFWString(data, "deny")
    # result is stored into a json object
    json_obj = { 
        "allow_all": allow_output["all"],
        "allow_tag": allow_output["tag"],
        "allow_sa": allow_output["sa"],
        "deny_all": deny_output["all"],
        "deny_tag": deny_output["tag"],
        "deny_sa": deny_output["sa"]
        }
    # # results are dumped to stdout 
    print(json.dumps(json_obj, indent=4))

# Assembles Flat Map for Ingress FW rules on GCP to be consued by terraform
def assembleIngressFWString(data, k):
    result = {
        "all": "",
        "tag": "",
        "sa": ""
    }
    if k not in data:
        return result

    for x in data[k]:
        output = ""
        output = output + x + "=="
        fw = data[k][x]

        output = output + flattenString(fw, "description")
        output = output + flattenList(fw, "source_ranges")
        output = output + flattenString(fw, "protocol")
        output = output + flattenList(fw, "ports")
        output = output + flattenString(fw, "priority", default="1000")

        if ("target_service_account" in fw ) or ("source_service_account" in fw):
            output = output + flattenString(fw, "target_service_account")
            output = output + flattenString(fw, "source_service_account")

            result["sa"]= result["sa"] + output + "|"
        elif ("target_tags" in fw) or ("source_tags" in fw):
            output = output + flattenList(fw, "target_tags")
            output = output + flattenList(fw, "source_tags")

            result["tag"]= result["tag"] + output + "|"
        else:
            result["all"]= result["all"] + output + "|"

    return result

# Assembles Flat Map for Egress FW rules on GCP to be consued by terraform
def assembleEgressFWString(data, k):
    result = {
        "all": "",
        "tag": "",
        "sa": ""
    }
    if k not in data:
        return result

    for x in data[k]:
        output = ""
        output = output + x + "=="
        fw = data[k][x]
        output = output + flattenString(fw, "description")
        output = output + flattenList(fw, "destination_ranges")
        output = output + flattenString(fw, "protocol")
        output = output + flattenList(fw, "ports")
        output = output + flattenString(fw, "priority", default="1000")

        if "target_service_accounts" in fw:
            result["sa"]= result["sa"] + fw["target_service_accounts"] + "|"
        elif "target_tags" in fw:
            result["tag"]= result["tag"] + flattenList(fw, "target_tags") + "|"
        else:
            result["all"]= result["all"] + output + "|"

    return result

def flattenList(data, k):
    output = ""
    if k not in data:
        return ","

    for v in data[k]:
        output = output + str(v) + "+"
    
    return output + ","

def flattenString(data, k, **kwargs):
    if k in data:
        return str(data[k]) + ","
    else:
        if "default" in kwargs:
            return kwargs["default"] + ","
        else:
            return ","

def main():
    """ Entry point """
    # parsing arguments
    args = _parse_argument()

    args.func(args)

    return 0


if __name__ == '__main__':
    try:
        exit(main())
    except Exception as e:
        eprint('Caught an unexpected exception: {}'.format(e))
        exit(1)
