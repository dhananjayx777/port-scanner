import argparse
import sys

from port_scanner import PortScanner


def parse_args():
    parser = argparse.ArgumentParser(description="Simple TCP Port Scanner")
    parser.add_argument("target", help="Target IP address or hostname")
    parser.add_argument("-s", "--start-port", type=int, default=1)
    parser.add_argument("-e", "--end-port", type=int, default=1024)
    parser.add_argument("-t", "--threads", type=int, default=100)
    parser.add_argument("-T", "--timeout", type=float, default=1.0)
    parser.add_argument("-b", "--banner", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()

    scanner = PortScanner(
        target=args.target,
        start_port=args.start_port,
        end_port=args.end_port,
        threads=args.threads,
        timeout=args.timeout,
        grab_banners=args.banner,
    )

    print(f"Scanning {args.target} ports {args.start_port}-{args.end_port} ...")
    result = scanner.run()

    if result is None:
        print(f"Could not resolve target: {args.target}")
        sys.exit(1)

    print(f"Target: {result['target']} ({result['ip']})")
    print(f"Scan completed in {result['elapsed']:.2f} seconds")
    print(f"Open ports found: {len(result['open_ports'])}")
    print("-" * 45)

    if not result["open_ports"]:
        print("No open ports found.")
        return

    print(f"{'PORT':<10}{'SERVICE':<15}BANNER")
    for port, service, banner in result["open_ports"]:
        print(f"{port:<10}{service:<15}{banner}")


if __name__ == "__main__":
    main()