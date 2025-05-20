## AuthN using profile in config
##        it can be from 'oci session authenticate' 
##  (or) 
##        api-key of user-account/generic account(of OCI)

## .oci/config contains below like content
## key_file = oci_api_key.pem
## tenancy = ocid1.tenancy.oc1..
## region = us-phoenix-1
## security_token_file = token	## specific to -> oci session authenticate
## user = ocid1.user.oc1.. 	## specific to -> generic user


## using profile
config = oci.config.from_file("~/.oci/config", "<profile-name>") ## example-profile for a tenancy
compute_client = oci.core.ComputeClient(config)
virtual_network_client = oci.core.VirtualNetworkClient(config)

## using signer( Instance Principle )
signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
identity_client = oci.identity.IdentityClient(config={}, signer=signer)
compute_client = oci.core.ComputeClient(config={}, signer=signer)
network_client = oci.core.VirtualNetworkClient(config={}, signer=signer)
fs_client = oci.file_storage.FileStorageClient(config={}, signer=signer)
object_storage_client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)

streaming_endpoint = f"https://streaming.{region}.oci.oraclecloud.com"  ## for each region diff - ep
streaming_client = oci.streaming.StreamAdminClient(config={}, signer=signer, service_endpoint=streaming_endpoint)

usage_api_client = oci.usage_api.UsageapiClient(config={}, signer=signer)
usage_api_client.base_client.endpoint = f"https://usageapi.{home_region}.oci.oraclecloud.com"


## Basic details of tenancy ====================
tenancy_details = identity_client.get_tenancy(tenancy_id=ROOT_COMPARTMENT_ID)
regions = identity_client.list_region_subscriptions(tenancy_id=ROOT_COMPARTMENT_ID).data

region_list =  [ rg.region_name for rg in regions ]
for region in region_list:
	identity_client.base_client.set_region(region)
	availability_domains = identity_client.list_availability_domains(compartment_id=ROOT_COMPARTMENT_ID)
	ad_list.append({"region":region,"ads":[ad.name for ad in availability_domains.data]})

compartments = oci.pagination.list_call_get_all_results(
        identity_client.list_compartments,
        compartment_id=ROOT_COMPARTMENT_ID,
        compartment_id_in_subtree=True,
        access_level="ACCESSIBLE",
        lifecycle_state=oci.identity.models.Compartment.LIFECYCLE_STATE_ACTIVE
    )
compartment_map = { compartment.id:compartment.name for compartment in compartments.data}
## --------------------------------

instance_details = compute_client.get_instance(INSTANCE_ID).data 
instances_list = oci.pagination.list_call_get_all_results(
                compute_client.list_instances,compartment_id=compartment_id).data

compute_client.base_client.set_region(image_id.split('.')[3])
image_details = compute_client.get_image(image_id=image_id).data

vnic_attachment_details  = compute_client.get_vnic_attachment(vnic_attachment_id).data
vnic_attachments_4instance = compute_client.list_vnic_attachments(compartment_id=COMPARTMENT_ID, instance_id=INSTANCE_ID).data
vnic_attachments_4compartment = oci.pagination.list_call_get_all_results(
                compute_client.list_vnic_attachments, compartment_id=compartment_id).data

vnic_details = network_client.get_vnic(vnic_id).data

subnet_details = network_client.get_subnet(subnet_id).data
vcn_details = network_client.get_vcn(subnet_details.vcn_id).data
private_ips = oci.pagination.list_call_get_all_results(
                network_client.list_private_ips, subnet_id=subnet_id).data
public_ips = oci.pagination.list_call_get_all_results(
                network_client.list_public_ips, scope="REGION", compartment_id=compartment_id).data

fs_client.base_client.set_region(dict["region"])
file_systems = fs_client.list_file_systems(compartment_id=compartment, availability_domain=ad)

namespace = object_storage_client.get_namespace(compartment_id=ROOT_COMPARTMENT_ID).data
buckets = object_storage_client.list_buckets(namespace_name=namespace,compartment_id=compartment_id).data
bucket = object_storage_client.get_bucket(namespace_name=namespace,bucket_name=bucket_details.name).data


streams = oci.pagination.list_call_get_all_results(streaming_client.list_streams ,compartment_id=compartment_id).data 
for strm in streams:
	stream_pool = streaming_client.get_stream_pool(strm.stream_pool_id).data
	stream = streaming_client.get_stream(strm.id).data 

## cost usage
try:
    params=oci.usage_api.models.RequestSummarizedUsagesDetails(
	#tenant_id=signer.tenancy_id,
	tenant_id=ROOT_COMPARTMENT_ID,
	time_usage_started=start_date.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
	time_usage_ended=end_date.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
	granularity="MONTHLY",
	#is_aggregate_by_time=True,
	group_by=["resourceId"],
	filter=oci.usage_api.models.Filter(
	    operator="AND",
	    dimensions=[ 
		oci.usage_api.models.Dimension(key="service", value="BLOCK_STORAGE")  ]
	))
    request_summarized_usages_response = usage_api_client.request_summarized_usages(request_summarized_usages_details=params)
    dict = oci.util.to_dict(request_summarized_usages_response.data)
    cost_df = pd.DataFrame(dict['items'])
except: pass

## ------
announcement_client = oci.announcements_service.AnnouncementClient(config={}, signer=signer)
announcement_details = announcement_client.get_announcement(a_id).data
announcements = announcement_client.list_announcements(
        compartment_id = ROOT_COMPARTMENT,
        time_one_earliest_time = (today - timedelta(days=1)).strftime(%Y-%m-%dT%H:%M:%S.%fZ")
        time_one_latest_time = today.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    ).data
    announcement_ids = [announcement.id for announcement in announcements.items]
## ------
limits_client = oci.limits.LimitsClient(config={}, signer=signer)
services = oci.pagination.list_call_get_all_results(limits_client.list_services, compartment_id=compartment_id).data
for service in services:
	sname = service.get("name")
	limit_definition = oci.pagination.list_call_get_all_results(limits_client.list_limit_definitions, compartment_id=compartment_id, service_name=sname).data
	limit_value = oci.pagination.list_call_get_all_results(limits_client.list_limit_values, compartment_id=compartment_id, service_name=sname).data
resource_usage =  limits_client.get_resource_availability(service_name=service_name, limit_name=limit_name, compartment_id=compartment_id).data
## ------
