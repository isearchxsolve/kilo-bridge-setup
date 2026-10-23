import lane_tools as T

lane = T.Lane("timebucks", "tabs_list")
with T.session(lane) as client:
    tabs = client.list_tabs()
    print("ALL TABS COUNT:", len(tabs))
    for t in tabs:
        print("  ->", t)
