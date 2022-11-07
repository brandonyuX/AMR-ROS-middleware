from aphyt import omron

eip_instance = omron.n_series.NSeries()
eip_instance.connect_explicit('192.168.250.1')
eip_instance.register_session()
eip_instance.update_variable_dictionary()