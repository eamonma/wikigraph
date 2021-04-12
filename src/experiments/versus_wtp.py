import timeit
import math
import os


def time_versus(us: str = "print('hello, world')",
                them: str = "[i*i for i in range(10000)]",
                options: dict = dict(),
                globalz = None
                ) -> dict:
    """Pit one of our functions against one of their functions, time-wise.
    Default options: 
    | prints results 
    | run each 1 time 
    | show multiplier 
    | show orders of magnitude
    | do not show difference
    """
    options_defaults = {
        "no_io": False,
        "times": 1,
        "show_laps": True,
        "order_of_magnitude": True,
        "show_diff": False,
    }

    options = {option: options[option] if option in options else options_defaults[option]
               for option in options_defaults}

    times = options["times"]

    f_time = timeit.timeit(us, number=times, globals=globalz if globalz else globals())
    g_time = timeit.timeit(
        them, number=times, globals=globalz if globalz else globals())

    if not options["no_io"]:
        print(f"\n'{us}' versus '{them}', {times} time{'s' if times > 1 else ''}:")
        print(f"Our implementation:          {f_time:3.5f} seconds")
        print(f"Their implementation:        {g_time:3.5f} seconds")

        if options["show_laps"]:
            print(f"Times faster:                {g_time / f_time:.5f}")
        if options["show_diff"]:
            print(
                f"Diffrence:                   {abs(g_time - f_time):.5f}")
        if options["order_of_magnitude"]:
            oom = round(abs(math.log(g_time / f_time, 10)))
            print(
                f"{'Orders of magnitude:' if oom > 1 else 'Order of magnitude: '}         {oom}")
        print("")

    return {
        us: f_time,
        them: g_time
    }


def diff_lists(us: list, them: list, print: bool = True, delete: bool = True) -> list:
    """Compare two potentially large lists by writing them to disk and diff'ing them
    """
    f = open("us.txt", "w")
    g = open("them.txt", "w")

    f.write("\n".join(us))
    g.write("\n".join(them))

    diffs = os.popen("diff us.txt them.txt").read()
    diffs_list = diffs.split("\n")

    if io:
        diffs_joined_list = []
        for i in range(len(diffs_list) - 1):
            if not i % 2:
                diffs_joined_list.append(
                    diffs_list[i] + "\n" + diffs_list[i + 1] + "\n\n")  
        print("".join(diffs_joined_list))

    return_list = []

    for i in range(len(diffs_list) - 1):
        if not i % 2:
            return_list.append(
                diffs_list[i] + ": " + diffs_list[i + 1])

    if delete:
        if os.path.exists("us.txt"):
            os.remove("us.txt")

        if os.path.exists("them.txt"):
            os.remove("them.txt")

    return return_list


if __name__ == "__main__":
    # load files
    from wikitext import collect_links_wikitext
    with open('../data/raw/reduced/hundredk.xml', 'r') as reader:
        wikitext = reader.read()

    # demo time_versus
    import wikitextparser as wtp
    time_versus("collect_links_wikitext(wikitext)",
                "wtp.parse(wikitext)",
                {"times": 1})

    # demo diff_lists
    diff_lists([item for item in collect_links_wikitext(wikitext) if item],
               [l.title for l in wtp.parse(wikitext).wikilinks if l.title], io=False)
