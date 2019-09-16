import arrow

__all__ = ["moment"]


class Moment(arrow.Arrow):
    @property
    def second_timestamp(self):
        return self.timestamp

    # 毫秒
    @property
    def millisecond_timestamp(self):
        return self.timestamp * 1000 + int(self.microsecond / 1000)

    # 微妙
    @property
    def microsecond_timestamp(self):
        return self.timestamp * 1000000 + self.microsecond


class MomentFactory(arrow.ArrowFactory):
    def get(self, *args, **kwargs):
        if args and isinstance(args[0], int) and len("{}".format(args[0])) == 13:
            args = (args[0] * 1000 / 1000000.0,) + args[1:]
        return super().get(*args, **kwargs)


moment = MomentFactory(Moment)
