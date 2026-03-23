from storage_site_input import StorageSiteInput


def build_test_data() -> list[StorageSiteInput]:
    return [
        StorageSiteInput(
            site_id="ST001",
            site_name="Taipei Main Warehouse",
            capacity_tons=1250.5,
            is_active=True,
        ),
        StorageSiteInput(
            site_id="ST002",
            site_name="Taichung Backup Storage",
            capacity_tons=860.0,
            is_active=False,
        ),
        StorageSiteInput(
            site_id="ST003",
            site_name="Kaohsiung Cold Storage",
            capacity_tons=1430.25,
            is_active=True,
        ),
    ]


def run_demo() -> None:
    test_data = build_test_data()
    print("StorageSiteInput demo data:")
    for item in test_data:
        print(item)


if __name__ == "__main__":
    run_demo()
