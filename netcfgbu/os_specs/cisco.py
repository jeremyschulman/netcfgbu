cisco_spec = {"pre_get_config": "terminal length 0"}

cisco_asa_spec = {"pre_get_config": "terminal pager 0"}

cisco_aireos_spec = {
    "get_config": "show run-config commands",
    "pre_get_config": "config paging disable",
}
