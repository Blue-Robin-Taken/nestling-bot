import main
from Other import maths


@main.flip.error
async def main(ctx, err):
    await ctx.respond(err)