from NetworkChecker import NetworkChecker 


if __name__ == "__main__":
    nc = NetworkChecker()
    print(nc.test_latency("1.1.1.1"))
    print(nc.test_latency("8.8.8.8"))
    print(nc.test_latency("111.1111.1.1"))
    