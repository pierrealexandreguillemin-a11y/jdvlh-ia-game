import asyncio
import time
import statistics
from pathlib import Path
import sys
import yaml
from jdvlh_ia_game.services.cache import CacheService
from jdvlh_ia_game.services.narrative import NarrativeService

sys.path.append("src")

# Load config
CONFIG_PATH = Path(__file__).parent / "src" / "jdvlh_ia_game" / "config" / "config.yaml"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


async def bench_cache():
    print("=== BENCH CACHE ===")
    cache = CacheService()
    times = []
    locations = ["la Comté", "Fondcombe", "les Mines de la Moria"]
    for _ in range(10):
        start = time.time()
        for loc in locations:
            _ = cache.get_location_data(loc)
        duration = time.time() - start
        times.append(duration)
    print(f"Moyenne cache 30 lookups: {statistics.mean(times) * 1000:.0f} ms")


async def bench_narrative(num_tests=5):
    print("=== BENCH NARRATIVE ===")
    narrative = NarrativeService()
    context = "Test context."
    history = []
    choice = "Explorer"
    blacklist = []
    times = []
    for i in range(num_tests):
        start = time.time()
        _ = await narrative.generate(context, history, choice, blacklist)
        duration = time.time() - start
        times.append(duration)
        print(f"Test {i + 1}: {duration * 1000:.0f} ms")
    print(f"Moyenne narrative: {statistics.mean(times) * 1000:.0f} ms")


async def main():
    await bench_cache()
    await bench_narrative()


if __name__ == "__main__":
    asyncio.run(main())
