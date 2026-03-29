"""CLI entry point — starts the uvicorn server."""

import uvicorn


def main():
    uvicorn.run(
        "dns_converter.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
