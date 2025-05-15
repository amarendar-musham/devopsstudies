## AuthN using profile in config
##        it can be from 'oci session authenticate' 
##  (or) 
##        api-key of user-account/generic account(of OCI)

## using profile
config = oci.config.from_file("~/.oci/config", "<profile-name>") ## example-profile for a tenancy
compute_client = oci.core.ComputeClient(config)
virtual_network_client = oci.core.VirtualNetworkClient(config)

## using signer( Instance Principle )
signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
identity_client = oci.identity.IdentityClient(config={}, signer=signer)
compute_client = oci.core.ComputeClient(config={}, signer=signer)

## ---------------------------
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
vnic_attachment = compute_client.get_vnic_attachment(vnic_attachment_id).data
vnics = compute_client.list_vnic_attachments(compartment_id=COMPARTMENT_ID, instance_id=INSTANCE_ID).data
