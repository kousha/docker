#!/usr/bin/env python

import argparse
import logging
import sys
import urllib2

from boto import ec2
from boto import vpc
import boto


"""
Create/update AWS security groups for Stackdriver enpoint monitoring IPs.

This python script that updates/creates security groups in every VPC that allow
Stackdriver IPs access for probing.

You need to pass in your Stackdriver API key with '-k'.
You need to pass in your AWS credentials via environment variables:
    AWS_SECRET_ACCESS_KEY=<access_key_id>
    AWS_SECRET_ACCESS_KEY=<secret_access_key>
"""

__author__ = "Kousha Najafi <kousha@lazyhack.com>"

logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def revoke(conn, sg, rule, grant):
    logger.info("Revoking grant: (%r, %r, %r)", sg, rule, grant)
    try:
        conn.revoke_security_group(
                group_id=sg.id,
                ip_protocol=rule.ip_protocol,
                from_port=rule.from_port,
                to_port=rule.to_port,
                src_security_group_group_id=grant.group_id,
                cidr_ip=grant.cidr_ip)
    except boto.exception.EC2ResponseError, e:
        logger.error("Error revoking grant: (%r, %r, %r)", sg, rule, grant)


def main(argv):
    parser = argparse.ArgumentParser(
            description=("Create/Update a security group with Stackdriver IPs "
            "used for endpoint monitoring."),
            fromfile_prefix_chars="@")
    parser.add_argument("-s", "--security_group",
            default="stackdriver-endpoint-monitoring",
            help="Name of the security group to create/update.")
    parser.add_argument("--description",
            default="Security group containing Stackdriver endpoint IPs.",
            help="Description for the security group.")
    parser.add_argument("-r", "--region", default="us-east-1",
            help="The AWS region to use.")
    parser.add_argument("-k", "--stackdriver_api_key",
            required=True,
            help="API Key to use with Stackdriver API")
    parser.add_argument("-v", "--verbose", action="count")
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.FATAL - (args.verbose * 10))

    vpc_conn = vpc.connect_to_region(args.region)
    if vpc_conn is None:
        logger.fatal("Invalid AWS Region: %r", args.region)
        sys.exit(1)
    all_security_groups = vpc_conn.get_all_security_groups()
    all_vpcs  = vpc_conn.get_all_vpcs()

    vpc_set = set(vpc.id for vpc in all_vpcs)
    logger.info("VPCs: %r", vpc_set)

    # Existing security groups with the given name
    existing_security_groups = [ sg for sg in all_security_groups if sg.name == args.security_group ]
    logger.info("Existing Security Groups: %r", existing_security_groups)

    # VPCs without the given security group
    nvpcs = vpc_set - set(sg.vpc_id for sg in existing_security_groups)
    logger.info("VPCs that need the new group: %r", nvpcs)

    for v in nvpcs:
        logger.info("Creating new security group: name=%r, vpc_id=%r", args.security_group, v)
        existing_security_groups.append(
                vpc_conn.create_security_group(args.security_group, args.description, vpc_id = v))

    logger.info("Security groups to modify: %r", existing_security_groups)

    # Grab Stackdriver IPs from Stackdriver API
    url = "https://api.stackdriver.com/v0.2/endpoints/ips/?apikey=%s" % args.stackdriver_api_key
    try:
          result = urllib2.urlopen(url)
          result_body = result.readlines()
          import json
          parsed_json = json.loads(result_body[0])

    except urllib2.URLError, e:
          logger.error(e)

    cidr_ips = [ d["ip"] + "/32" for d in parsed_json["data"]]
    cidr_ip_set = set(cidr_ips)
    logger.info("Stackdriver IPs: %r", cidr_ips)


    def grantShouldExist(sg, rule, grant):
        logger.debug("grantShouldExist: (%r, %r, %r, %r)", rule.ip_protocol, rule.from_port, rule.to_port, grant.cidr_ip in cidr_ip_set)
        ret = (
                rule.ip_protocol == "tcp" and
                rule.from_port == "0" and
                rule.to_port == "65535" and
                grant.cidr_ip in cidr_ip_set
              )
        return ret


    for sg in existing_security_groups:
        existing_cidr_ip_set = set()
        try:
            # Revoke old grants
            for rule in sg.rules:
                for grant in rule.grants:
                    if grantShouldExist(sg, rule, grant):
                        existing_cidr_ip_set.add(grant.cidr_ip)
                    else:
                        revoke(vpc_conn, sg, rule, grant)

            # Add new grants
            for cidr_ip in cidr_ip_set - existing_cidr_ip_set:
                logger.info("Adding rule: ip=%r, sg=%r, vpc=%r", cidr_ip, sg.id, sg.vpc_id)
                sg.authorize(
                        ip_protocol="tcp",
                        from_port=0,
                        to_port=65535,
                        cidr_ip=cidr_ip)

        except boto.exception.EC2ResponseError, e:
            logger.error("Boto Exception: %r", e)

    logger.info("Done.")


if __name__ == "__main__":
    main(sys.argv)
