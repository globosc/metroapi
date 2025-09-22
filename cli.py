#!/usr/bin/env python3
import argparse
import json
import sys
import logging
from metro_service import MetroService
from config import get_config

def setup_logging(verbose: bool):
    """Configura el logging según el nivel de verbosidad"""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s'
    )

def main():
    parser = argparse.ArgumentParser(
        description="Cliente CLI para consultar el estado del Metro de Santiago"
    )

    parser.add_argument(
        "--format",
        choices=["json", "text", "status"],
        default="text",
        help="Formato de salida (default: text)"
    )

    parser.add_argument(
        "--summary",
        action="store_true",
        help="Mostrar resumen completo con estadísticas"
    )

    parser.add_argument(
        "--failed-only",
        action="store_true",
        help="Mostrar solo líneas con problemas"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Salida verbosa con logs de debug"
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    metro_service = MetroService()

    try:
        if args.summary:
            # Mostrar resumen completo
            summary = metro_service.get_summary()
            if summary is None:
                print("❌ No se pudo obtener el estado del metro", file=sys.stderr)
                sys.exit(1)

            if args.format == "json":
                print(json.dumps(summary, indent=2, ensure_ascii=False))
            else:
                print_summary(summary)

        elif args.failed_only:
            # Mostrar solo líneas con problemas
            failed_stations = metro_service.get_failed_stations()
            if failed_stations is None:
                print("❌ No se pudo obtener el estado del metro", file=sys.stderr)
                sys.exit(1)

            if not failed_stations:
                print("✅ Todas las líneas del metro están operativas")
            else:
                print_failed_stations(failed_stations, args.format)

        else:
            # Mostrar estado normal
            if args.format == "json":
                status = metro_service.get_lines_status()
                if status is None:
                    print('{"error": "No se pudo obtener el estado del metro"}')
                    sys.exit(1)
                print(json.dumps({"metro": status}, indent=2))

            elif args.format == "status":
                status = metro_service.get_lines_status()
                if status is None:
                    sys.exit(1)
                for line, line_status in status.items():
                    print(f"{line}: {line_status}")

            else:  # text format
                display_text = metro_service.format_for_display()
                if display_text is None:
                    print("❌ No se pudo obtener el estado del metro", file=sys.stderr)
                    sys.exit(1)
                print(display_text)

    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}", file=sys.stderr)
        sys.exit(1)

def print_summary(summary):
    """Imprime el resumen en formato texto"""
    print("📊 Resumen del Metro de Santiago:")
    print(f"   Total de líneas: {summary['summary']['total_lines']}")
    print(f"   Líneas operativas: {summary['summary']['operational_lines']}")
    print(f"   Líneas con problemas: {summary['summary']['failed_lines']}")

    overall_emoji = "✅" if summary['summary']['overall_status'] == "ok" else "⚠️"
    print(f"   Estado general: {overall_emoji} {summary['summary']['overall_status']}")
    print()

    # Estado por línea
    print("📍 Estado por línea:")
    for line, status in summary['status'].items():
        emoji = "✅" if status == "ok" else "❌"
        print(f"   {line}: {emoji}")

    # Estaciones con problemas
    if summary['failed_stations']:
        print("\n⚠️  Estaciones con problemas:")
        for line, stations in summary['failed_stations'].items():
            print(f"   {line}: {', '.join(stations)}")

def print_failed_stations(failed_stations, format_type):
    """Imprime las estaciones con problemas"""
    if format_type == "json":
        print(json.dumps(failed_stations, indent=2, ensure_ascii=False))
    else:
        print("⚠️  Líneas con problemas:")
        for line, stations in failed_stations.items():
            print(f"   {line}: {', '.join(stations)}")

if __name__ == "__main__":
    main()