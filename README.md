# Terraform Flatten
An opinionated way of passing IAM Permissions down to modules for processing. This app does validation and than flattens the MAP, in order for it to be processed by terraform modules. 

Currently supports following:
- Flattening IAM permissions
- Flattening Compute Firewall Ingress/Egress rules
- Json Schema is validated against draft-07

## Schema

### IAM
The expected input for iam permissions should follow:

```json
{
    "roles/editor": ["user:user@muvaki.com","serviceAccount:sa@muvaki.com"],
    "roles/viewer": ["domain:domain@muvaki.com", "group:group@muvaki.com"],
    "projects/muvaki-qa/roles/secrets": ["user:admin@muvaki.com"]
}
```

Valid role values have to match following regex:
1. ^roles/[a-zA-Z0-9_-]+$
2. ^projects/[a-zA-Z0-9-]+/roles/[a-zA-Z0-9_.+-]+$

Valid account permission can have one of the following headers split by : and email address.
1. user
2. serviceAccount
3. domain
4. group

### Firewall

Schema for Ingress and Egress are slightly different. It is assumed that the json passed to fw is egress, however, if you want to pass ingress json than pass --ingress flag.

The Terraform page for [google_compute_firewall]((https://www.terraform.io/docs/providers/google/r/compute_firewall.html)) does a good explanantion of expalining the different permissible options allowed for ingress and egress.

#### Egress

Check the example folder for more **detailed** use cases.

```json
{
    "allow": {
        "web": {
            ...
            ...
            ...
        }
    },
    "deny": {
        "ssh": {
            ...
            ...
            ...
        }
    }
}
```

1. The two main components of passing rules fall under the "allow" or "deny" headers. These define the permissible rules under the respective categories.
2. Second header defines the unique name for the firewall. The names when created are appended with following: <vpc-name>-<allow/deny>-<fw-name>
3. under this tier more specific level configuration is set (egress/ingress):

#### Egress

| Name | Description | Type | Pattern | Default | Required | Conflict |
|------|-------------|------|---------|---------|----------|----------|
| description | FW Rule Description | string | "\^[a-zA-Z0-9 \\-_]*$" | - | no | - |
| protocol | Protocol to define  | string| tcp,udp,icmp,esp,ah,sctp,all or any Protocol number | - | yes | - |
| ports |  Ports that apply for the permission. This is required if protocol is either tcp/udp | integer | 0-65535 | - | no | - |
| disabled | Weather to disable firewall rule | string | "true or false" | false | no | - |
| priority | Relative priorities determine precedence of conflicting rules. Lower value of priority implies higher precedence | integer | 0-65535 | 1000 | no | - |
| destination_ranges | if destination ranges are specified, the firewall will apply only to traffic that has destination IP address in these ranges | list | IPv4 CIDR (string) | - | no | - |
| target_service_account | A service Account located in the network that may make network connections as specified. | string | email address | - | no | target_tags |
| target_tags | A list of instance tags indicating set of instances located in the network that may make network connections as specified | list | text | - | no | target_service_account |

#### Ingress

| Name | Description | Type | Pattern | Default | Required | Conflict |
|------|-------------|------|---------|---------|----------|----------|
| description | FW Rule Description | string | "\^[a-zA-Z0-9 \\-_]*$" | - | no | - |
| protocol | Protocol to define  | string| tcp,udp,icmp,esp,ah,sctp,all or any Protocol number | - | yes | - |
| ports |  Ports that apply for the permission. This is required if protocol is either tcp/udp | integer | 0-65535 | - | no | - |
| disabled | Weather to disable firewall rule | string | "true or false" | false | no | - |
| priority | Relative priorities determine precedence of conflicting rules. Lower value of priority implies higher precedence | integer | 0-65535 | 1000 | no | - |
| source_ranges | If source ranges are specified, the firewall will apply only to traffic that has source IP address in these ranges | list | IPv4 CIDR (string) | - | no | - |
| target_service_account | A service Account located in the network that may make network connections as specified. | string | email address | - | no | target_tags, source_tags |
| source_service_account | If source service accounts are specified, the firewall will apply only to traffic originating from an instance with attached service account. | string | email address | - | no | target_tags, source_tags |
| target_tags | A list of instance tags indicating set of instances located in the network that may make network connections as specified | list | text | - | no | target_service_account, source_service_account |
| source_tags |  If source tags are specified, the firewall will apply only to traffic with source IP that belongs to a tag listed in source tags | list | text | - | no | target_service_account, source_service_account |


## Usage
The output from flatten can be fed into Terraform **[External Data Source](https://www.terraform.io/docs/providers/external/data_source.html)** and be used in modules as desired. Currently, there is support for IAM permissions and Firewall Ingress/Egress rules. 

### IAM
To execute flattening of **IAM permission**, pass the following parameters.

```sh
docker run muvaki/flatten:0.0.1 iam '{"roles/editor":["user:a@muvaki.com","user:b@muvaki.com"],"roles/viewer":["user:z@muvaki.com","user:r@muvaki.com"]}'
```

resulting command will generate following output
```json
{
    "output": "roles/viewer|user:z@muvaki.com user:r@muvaki.com ,roles/editor|user:a@muvaki.com user:b@muvaki.com ,"
}
```

### Firewall
To execute flattening of **Firewall Egress permission**, pass the following parameters.

```sh
docker run muvaki/flatten:0.0.1 fw '{"deny":{"ssh":{"description":"SSH","destination_ranges":["192.160.10.0/24","10.0.0.0/16"],"priority":11,"protocol":"tcp","ports": [90]}}}'
```

resulting command will generate following output
```json
{
    "allow_all": "",
    "allow_tag": "",
    "allow_sa": "",
    "deny_all": "ssh==SSH,192.160.10.0/24+10.0.0.0/16+,tcp,90+,11,|",
    "deny_tag": "",
    "deny_sa": ""
}
```

**Ingress** permissions are similarly passed with flag --ingress
```sh
docker run muvaki/flatten:0.0.1 fw --ingress '{"allow":{"test":{"description":"SSH","protocol":"all","source_ranges":["192.160.10.0/24","10.0.0.0/16"]}}}'
```

resulting command will generate following output
```json
{
    "allow_all": "test==SSH,192.160.10.0/24+10.0.0.0/16+,all,,1000,|",
    "allow_tag": "",
    "allow_sa": "",
    "deny_all": "",
    "deny_tag": "",
    "deny_sa": ""
}
```