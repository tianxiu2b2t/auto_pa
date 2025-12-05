import anyio
import core.appgallery as appgallery

async def main():
    await appgallery.main()
    

if __name__ == "__main__":
    anyio.run(main)
