from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    use_redis: bool


@dataclass
class Miscellaneous:
    other_params: str = None


@dataclass()
class Qiwi:
    secret_p2p_token: str


@dataclass
class Config:
    tg_bot: TgBot
    misc: Miscellaneous
    qiwi: Qiwi


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS"),
        ),
        misc=Miscellaneous(),
        qiwi=Qiwi(
            secret_p2p_token=env.str("QIWI_SECRET_P2P_TOKEN")
        )
    )
