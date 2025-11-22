if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.jdvlh_ia_game.core.game_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
