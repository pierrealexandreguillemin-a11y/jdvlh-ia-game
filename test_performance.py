"""
Test de performance simple pour analyser les temps de réponse Ollama
"""

import asyncio
import time
import statistics
import ollama


async def test_ollama_response_times():
    """Test les temps de réponse Ollama avec différents prompts"""

    print("=" * 70)
    print("TEST PERFORMANCE OLLAMA - JDVLH IA Game")
    print("=" * 70)

    test_prompts = [
        ("Court", "Decris la Comte en 1 phrase."),
        (
            "Moyen",
            "Raconte une aventure dans Fondcombe pour un enfant de 10 ans en 3 phrases.",
        ),
        (
            "Long",
            "Decris les Mines de la Moria de maniere detaillee et immersive pour enfants.",
        ),
    ]

    all_times = []

    for test_name, prompt in test_prompts:
        print(f"\n[TEST {test_name}] Prompt: {prompt[:50]}...")
        times = []

        for i in range(3):
            print(f"  Tentative {i+1}/3...", end=" ")
            start = time.time()

            try:
                response = ollama.generate(
                    model="llama3.2",
                    prompt=prompt,
                    options={"temperature": 0.7, "num_predict": 150},
                )
                duration = time.time() - start
                times.append(duration)
                all_times.append(duration)

                print(
                    f"OK - {duration*1000:.0f} ms ({len(response['response'])} chars)"
                )

            except Exception as e:
                print(f"ERREUR: {str(e)[:50]}")

        if times:
            avg = statistics.mean(times)
            print(
                f"  => Moyenne: {avg*1000:.0f} ms, Min: {min(times)*1000:.0f} ms, Max: {max(times)*1000:.0f} ms"
            )

    # Statistiques globales
    if all_times:
        print("\n" + "=" * 70)
        print("STATISTIQUES GLOBALES")
        print("=" * 70)
        print(f"Total tests:        {len(all_times)}")
        print(f"Temps moyen:        {statistics.mean(all_times)*1000:.0f} ms")
        print(f"Temps median:       {statistics.median(all_times)*1000:.0f} ms")
        print(f"Temps min:          {min(all_times)*1000:.0f} ms")
        print(f"Temps max:          {max(all_times)*1000:.0f} ms")

        sorted_times = sorted(all_times)
        p95 = sorted_times[int(len(sorted_times) * 0.95)]
        p99 = sorted_times[int(len(sorted_times) * 0.99)]

        print(f"P95:                {p95*1000:.0f} ms")
        print(f"P99:                {p99*1000:.0f} ms")

        print("\n" + "=" * 70)
        print("RECOMMANDATIONS")
        print("=" * 70)

        avg_ms = statistics.mean(all_times) * 1000

        if avg_ms < 3000:
            print("EXCELLENT - Temps de reponse tres rapide")
        elif avg_ms < 5000:
            print("BON - Temps de reponse acceptable pour un jeu narratif")
        elif avg_ms < 8000:
            print("MOYEN - Experience utilisateur correcte, optimisations possibles")
        else:
            print("LENT - Envisager:")
            print("  - Reduire num_predict (actuellement 300)")
            print("  - Augmenter le cache hit rate")
            print("  - Utiliser un modele plus leger")

        print("\nCache recommande: ~70% hit rate pour performances optimales")
        print("=" * 70)


if __name__ == "__main__":
    print("\nDemarrage test performance...")
    print("Assurez-vous qu'Ollama est actif!\n")

    asyncio.run(test_ollama_response_times())

    print("\nTest termine!")
