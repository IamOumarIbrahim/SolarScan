import os
import time
from solarscan.cli import run_scan
from solarscan.osm import parse_google_maps_url, query_osm_building
from solarscan.fixtures import capture_fixture

LINKS = [
    ("Dubai Sports City Parking ISD", "https://www.google.com/maps/place/Dubai+Sports+City+Parking+ISD/@25.0398306,55.2246444,150m/data=!3m1!1e3!4m6!3m5!1s0x3e5f6d74df6285ed:0xab03f69473ba84b3!8m2!3d25.0398413!4d55.2248916!16s%2Fg%2F11gnp99c2y?entry=ttu&g_ep=EgoyMDI2MDgwMi4wIKXMDSoASAFQAw%3D%3D"),
    ("S.S Lootah Residence JVC", "https://www.google.com/maps/place/S.S+Lootah+Residence+JVC/@25.0644293,55.2126804,269a,35y,3.77t/data=!3m1!1e3!4m6!3m5!1s0x3e5f6d007ff27b91:0x8e56fd7b8a8451d!8m2!3d25.0645787!4d55.2130164!16s%2Fg%2F11x5hstbh3?entry=ttu&g_ep=EgoyMDI2MDgwMi4wIKXMDSoASAFQAw%3D%3D"),
    ("Marasi House JVC", "https://www.google.com/maps/place/Marasi+House+-+JVC/@25.0564921,55.2051596,262a,35y,3.77t/data=!3m1!1e3!4m6!3m5!1s0x3e5f6d0b1dbb96bd:0x6b1e6365c8d455cc!8m2!3d25.0566875!4d55.2054375!16s%2Fg%2F11xt61dqbf?entry=ttu&g_ep=EgoyMDI2MDgwMi4wIKXMDSoASAFQAw%3D%3D"),
    ("Gunal Construction Site Office", "https://www.google.com/maps/place/R1098+%26+R1121%2F1+Gunal+Construction+(Hessa+Street)+Site+Office/@25.0733419,55.2160149,223a,35y,3.77t/data=!3m1!1e3!4m6!3m5!1s0x3e5f6d659ccf2fc1:0x11b6d1efc18d8597!8m2!3d25.0730091!4d55.2162038!16s%2Fg%2F11vdmtnbhg?entry=ttu&g_ep=EgoyMDI2MDgwMi4wIKXMDSoASAFQAw%3D%3D"),
    ("GEMS Soccer Field Al Barsha", "https://www.google.com/maps/place/GEMS+Soccer+Field+-+E44+-+Al+Barsha+South+First+-+Al+Barsha+-+Dubai/@25.0827018,55.217826,265a,35y,3.77t/data=!3m1!1e3!4m6!3m5!1s0x3e5f6c197ad4da75:0x4a3cdad3f6af0d21!8m2!3d25.0827321!4d55.218412!16s%2Fg%2F11bvthttj7?entry=ttu&g_ep=EgoyMDI2MDgwMi4wIKXMDSoASAFQAw%3D%3D"),
    ("Koukh Al Shay Al Barsha", "https://www.google.com/maps/place/Koukh+Al+Shay+%7C+Al+Barsha+2+-+Dubai/@25.0943926,55.213774,224a,35y,3.77t/data=!3m1!1e3!4m6!3m5!1s0x3e5f6d990e1ca243:0x5aa7c811f83eeabb!8m2!3d25.0947498!4d55.2140966!16s%2Fg%2F11w241gj9k?entry=ttu&g_ep=EgoyMDI2MDgwMi4wIKXMDSoASAFQAw%3D%3D"),
    ("Dubai Hills Business Park 1", "https://www.google.com/maps/place/Dubai+Hills+Estate+Business+Park+1/@25.1075546,55.2406272,223a,35y,3.77t/data=!3m1!1e3!4m6!3m5!1s0x3e5f6981c675b1af:0xa6de65faa9f04cf8!8m2!3d25.1075272!4d55.2408517!16s%2Fg%2F11fn64_8rx?entry=ttu&g_ep=EgoyMDI2MDgwMi4wIKXMDSoASAFQAw%3D%3D"),
    ("NAS Arena Dubai", "https://www.google.com/maps/place/NAS+Arena/@25.1296088,55.2929125,224a,35y,3.77t/data=!3m1!1e3!4m6!3m5!1s0x3e5f692e6040f0c5:0x900c4fbc553c26f5!8m2!3d25.1296089!4d55.2931766!16s%2Fg%2F11h4y3gyvs?entry=ttu&g_ep=EgoyMDI2MDgwMi4wIKXMDSoASAFQAw%3D%3D"),
    ("NEMA Pumps Intl LLC", "https://www.google.com/maps/place/NEMA+Pumps+Intl+LLC/@25.1755572,55.3639717,374a,35y,3.76t/data=!3m1!1e3!4m6!3m5!1s0x3e5f66fe9df274a3:0xec3315da271640c4!8m2!3d25.1755122!4d55.3640878!16s%2Fg%2F11bbwq9m0_?entry=ttu&g_ep=EgoyMDI2MDgwMi4wIKXMDSoASAFQAw%3D%3D"),
    ("Wasl Samari Residences", "https://www.google.com/maps/place/Wasl+-+Samari+Residences+(R472)/@25.1779524,55.3781885,374a,35y,3.76t/data=!3m1!1e3!4m6!3m5!1s0x3e5f66e1b7bbdb65:0xb29735d0f4435a9c!8m2!3d25.1786141!4d55.3781225!16s%2Fg%2F1pp2x0275?entry=ttu&g_ep=EgoyMDI2MDgwMi4wIKXMDSoASAFQAw%3D%3D"),
    ("TEKA Display ACE Festival City", "https://www.google.com/maps/place/TEKA+Display+in+ACE+Hardware+in+Dubai+Festival+City/@25.223755,55.35981,233a,35y,3.77t/data=!3m1!1e3!4m6!3m5!1s0x3e5f5dbf41a262a9:0xf9713010e5ae6139!8m2!3d25.2239339!4d55.3599168!16s%2Fg%2F11x6wlkvlc?entry=ttu&g_ep=EgoyMDI2MDgwMi4wIKXMDSoASAFQAw%3D%3D"),
    ("P S Festival City", "https://www.google.com/maps/place/P+S/@25.2219797,55.3553256,329a,35y,3.77t/data=!3m1!1e3!4m6!3m5!1s0x3e5f5d003742e919:0xa4b41e6ea7b2f11d!8m2!3d25.2224384!4d55.3569267!16s%2Fg%2F11yvg7m1yb?entry=ttu&g_ep=EgoyMDI2MDgwMi4wIKXMDSoASAFQAw%3D%3D"),
    ("Dubai Duty Free Distribution HQ", "https://www.google.com/maps/place/Dubai+Duty+Free+Distribution+HQ/@25.231314,55.3592067,554a,35y,3.76t/data=!3m1!1e3!4m6!3m5!1s0x3e5f5d77a59775bd:0x2f1763226593c6ec!8m2!3d25.2317193!4d55.359411!16s%2Fg%2F11b70gg8x8?entry=ttu&g_ep=EgoyMDI2MDgwMi4wIKXMDSoASAFQAw%3D%3D"),
    ("Virgin Mobile Terminal 3", "https://www.google.com/maps/place/Virgin+Mobile+-+Dubai+Duty+Free+-+Terminal+3/@25.2430263,55.3719373,783a,35y,3.75t/data=!3m2!1e3!5s0x3e5f5d97d4c18aa3:0x946dd901866aa368!4m6!3m5!1s0x3e5f5de85c1e5097:0x1e85e0e450829c9c!8m2!3d25.243431!4d55.372287!16s%2Fg%2F11txy05_hp?entry=ttu&g_ep=EgoyMDI2MDgwMi4wIKXMDSoASAFQAw%3D%3D"),
    ("Emirates Staff Accomodation EK2 A", "https://www.google.com/maps/place/Emirates+Airline+Staff+Accomodation+-+EK2+A+block/@25.2799214,55.4032918,311a,35y,3.77t/data=!3m1!1e3!4m6!3m5!1s0x3e5f5e8265ecf261:0xa6270bfa03251b40!8m2!3d25.2795805!4d55.4038278!16s%2Fg%2F11bxd_v0y1?entry=ttu&g_ep=EgoyMDI2MDgwMi4wIKXMDSoASAFQAw%3D%3D"),
    ("LTC International LLC", "https://www.google.com/maps/place/LTC+International+LLC/@25.2871216,55.4104013,261a,35y,3.77t/data=!3m1!1e3!4m6!3m5!1s0x3e5f5e9b0ad297cb:0xee3dd394c2202cca!8m2!3d25.2874413!4d55.4101455!16s%2Fg%2F11bbwmjh7_?entry=ttu&g_ep=EgoyMDI2MDgwMi4wIKXMDSoASAFQAw%3D%3D")
]

def main():
    out_dir = "reports/user_scans"
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs("validation/fixtures", exist_ok=True)

    print(f"Processing {len(LINKS)} Google Maps links with SolarScan...")
    for idx, (name, link) in enumerate(LINKS, 1):
        print(f"\n==================================================")
        print(f"[{idx}/{len(LINKS)}] {name}")
        print(f"Link: {link}")
        
        # Run solarscan scan directly using the Google Maps link
        pdf_out = run_scan(address=link, fmt="both", out_dir=out_dir)
        time.sleep(1.0)

if __name__ == "__main__":
    main()
