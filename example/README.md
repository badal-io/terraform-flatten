# Terraform Flatten Examples


## IAM

```json
{
    "roles/editor": ["user:user@muvaki.com","serviceAccount:sa@muvaki.com"],
    "roles/viewer": ["domain:domain@muvaki.com", "group:group@muvaki.com"],
    "projects/muvaki-qa/roles/secrets": ["user:admin@muvaki.com"]
}
```

## Firewall

### Egress

```json
{
    "allow": {
        "ranges": {
            "description": "This shows source ranges as the only setting enabled",
            "protocol": "all",
            "priority": 2000,
            "destination_ranges": ["192.160.0.0/32", "10.0.0.0/16"],
        },
        "tags": {
            "description": "This shows tags being used",
            "protocol": "udp",
            "ports": [1000],
            "disabled": "true",
            "target_tags": ["tag1", "tag2"]
        }
    },
    "deny": {
        "serviceAccount": {
            "description": "This shows service Account being used",
            "protocol": "tcp",
            "ports": [80,443],
            "target_service_account": "test@muvaki.com"
        },
        "rangeAndSA": {
            "description": "This shows source ranges and sa being used",
            "protocol": "tcp",
            "ports": [80,443],
            "destination_ranges": ["192.160.0.0/32", "10.0.0.0/16"],
            "target_service_account": "test@muvaki.com"           
        },
        "rangeAndtag": {
            "description": "This shows source ranges and tag being used",
            "protocol": "tcp",
            "ports": [80,443],
            "destination_ranges": ["192.160.0.0/32", "10.0.0.0/16"],
            "target_tags": ["tag1", "tag2"],          
        },
    }
}
```

### Ingress

```json
{
    "allow": {
        "ranges": {
            "description": "This shows source ranges as the only setting enabled",
            "protocol": "all",
            "priority": 2000,
            "source_ranges": ["192.160.0.0/32", "10.0.0.0/16"],
        },
        "tags": {
            "description": "This shows tags being used .. target and source... tags can also be used as target tags only",
            "protocol": "udp",
            "ports": [1000],
            "disabled": "true",
            "target_tags": ["target-tag1", "target-tag2"],
            "source_tags": ["source-tag1", "source-tag2"]
        },
        "serviceAccount": {
            "description": "This shows service Account being used... target and source.... service accounts cal also be used as target only",
            "protocol": "tcp",
            "ports": [80,443],
            "target_service_account": "target@muvaki.com",
            "source_service_account": "source@muvaki.com"
        },
    },
    "deny": {
        "rangeAndSA": {
            "description": "This shows source ranges and sa target being used together",
            "protocol": "tcp",
            "ports": [80,443],
            "destination_ranges": ["192.160.0.0/32", "10.0.0.0/16"],
            "target_service_account": "target@muvaki.com"
        },
        "rangeAndtag": {
            "description": "This shows source ranges and tag source/target being used together",
            "protocol": "tcp",
            "ports": [80,443],
            "destination_ranges": ["192.160.0.0/32", "10.0.0.0/16"],
            "target_tags": ["target-tag1", "target-tag2"],
            "source_tags": ["source-tag1", "source-tag2"]     
        },
    }
}
```