# Fights wtp
import wikitextparser as wtp
import timeit
import re
import math
# f = open("wtp.txt", "w")
# g = open("custom.txt", "w")

# f.write("\n".join([l.title for l in wtp.parse(wikitext).wikilinks if l.title]))
# g.write("\n".join([item for item in collect_links_wikitext(wikitext) if item]))

options_defaults = {
    "times": 1,
    "show_times": True,
    "order_of_magnitude": True,
    "show_diff": False,
}

with open('data/raw/hundredk.xml', 'r') as reader:
    wikitext = reader.read()

def time_versus(wikitext: str,
                us: str = "collect_links_wikitext(wikitext)",
                them: str = "wtp.parse(wikitext)",
                options: dict = options_defaults) -> dict:
    """Pit one of our functions against one of their functions, time-wise.
    """
    options = {option: options[option] if option in options else options_defaults[option]
               for option in options_defaults}

    times = options["times"]

    f_time = timeit.timeit(us, number=times, globals=globals())
    g_time = timeit.timeit(them, number=times, globals=globals())

    print(f"\n'{us}' versus '{them}', {times} time{'s' if times > 1 else ''}:")
    print(f"Our implementation:             {f_time:3.5f} seconds")
    print(f"Their implementation:           {g_time:3.5f} seconds")

    if options["show_times"]:
        print(f"Times faster:                   {g_time / f_time:.5f}")
    if options["show_diff"]:
        print(f"Diffrence:                      {abs(g_time - f_time):.5f}")
    if options["order_of_magnitude"]:
        oom = round(abs(math.log(g_time / f_time, 10)))
        print(
            f"{'Orders of magnitude:' if oom > 1 else 'Order of magnitude: '}            {oom}")
    print("")

    return {
        us: f_time,
        them: g_time
    }


# time_versus(wikitext, options={"times": 10})
