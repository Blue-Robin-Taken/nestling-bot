import main


@main.flip.error
def main(ctx, err):
    ctx.respond(err)
