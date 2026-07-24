"""Handle API errors with the typed exception hierarchy.

Requires the WEBSHARE_API_KEY environment variable.
"""

import webshare


def main() -> None:
    client = webshare.Webshare()
    try:
        client.subusers.get(999999999)
    except webshare.NotFoundError as err:
        print(f"Not found: {err.detail} (request id: {err.request_id})")
    except webshare.RateLimitError as err:
        print(f"Rate limited, retry later: {err.detail}")
    except webshare.PermissionDeniedError as err:
        # Every call can hit these account-state codes.
        if err.code == "2fa_needed":
            print("Two-factor authentication required; submit the code first.")
        elif err.code == "account_suspended":
            print("Account is suspended; see client.verification.get_suspension().")
        else:
            print(f"Forbidden: {err.detail}")
    except webshare.BadRequestError as err:
        print(f"Validation failed: {err.field_errors}")
    except webshare.APIConnectionError as err:
        print(f"Network problem: {err}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
