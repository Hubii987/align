from graphene_lab_gui.drivers.ESP8266DRV8825 import ESP8266DRV8825
from qubib.adapters.LocalSerial import LocalSerial
from qubib.adapters.NetworkSocket import NetworkSocket


def test_script(esp):
    """
    Test script with some test functions.

    :param esp: esp device
    :type esp: class
    """
    esp.stagetype = 'rot_200'
    print('Connected to the following device: {:s}'.format(esp.idn()))
    print('WIFI SSID: {:s}'.format(esp.get_ssid()))
    print('WIFI local IP: {:s}'.format(esp.get_local_ip()))
    print('WIFI SubNetMask: {:s}'.format(esp.get_subnetmask()))
    print('WIFI MAC addres: {:s}'.format(esp.get_macaddress()))
    print('WIFI gateway IP: {:s}'.format(esp.get_gateway_ip()))
    print('WIFI DNS IP: {:s}'.format(esp.get_dns_ip()))
    print('WIFI RSSI (dBm): {:d}'.format(esp.get_rssi()))
    print('WIFI channel: {:d}'.format(esp.get_wifi_channel()))
    print('WIFI status: {:d}'.format(esp.get_wifi_status()))
    print('WIFI status description: {:s}'.format(esp.get_wifi_status_desc()))
    esp.blink()
    # print(esp.blink_command())
    # esp.set_speed(2000)
    # esp.move_rel(-90)
    # time.sleep(1)
    # esp.set_speed(4000)
    # esp.move_rel(180)
    # time.sleep(1)
    # esp.set_speed(4000)
    # esp.move_rel(45)


def test_serial(com_port):
    """
    This function is an example function for the Sim900

    :param com_port: COM port
    :type com_port: str
    """
    from qubib.adapters.LocalSerial import LocalSerial

    adapter = LocalSerial(port=com_port, baudrate=9600)
    adapter.read_termination = '\r\n'        # CRLF
    adapter.write_termination = '\n'         # LF
    adapter.sleep_time = 0.005
    esp = ESP8266DRV8825(inst=adapter)

    test_script(esp)
    esp.close()


def test_network(ip, port):
    """
    This function is an example function for the Sim900

    :param ip: ip address
    :type ip: str
    :param port: port
    :type port: int
    """
    from qubib.adapters.NetworkSocket import NetworkSocket

    adapter = NetworkSocket(ip, port=port)
    adapter.timeout = 10
    adapter.write_termination = '\n'
    esp = ESP8266DRV8825(inst=adapter)

    test_script(esp)
    esp.close()


if __name__ == "__main__":
    # test_serial(com_port='/dev/cu.usbserial-1410')
    test_network(ip='10.42.0.63', port=5045)



