from austial import Injectable


@Injectable()
class AppService:
    def get_hello(self) -> dict:
        return {"message": "Hello from Austial Sample App, built with Austial!"}
