from storage_site_input import StorageSiteInput


def build_test_data() -> StorageSiteInput:
    return StorageSiteInput(
        site_id="ST001",
        site_name="Taipei Main Warehouse",
        capacity_tons=1250.5,
        is_active=True,
    )


def run_demo() -> None:
    test_data = build_test_data()
    print(test_data)


if __name__ == "__main__":
    run_demo()
