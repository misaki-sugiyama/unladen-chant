from tqdm import tqdm

class PBar(tqdm):
    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            try:
                kwargs['iterable'] = iter(args[0])
                try:
                    kwargs['total'] = len(args[0])
                except:
                    pass
            except:
                kwargs['total'] = args[0]
        super().__init__(disable=None, dynamic_ncols=True, unit_scale=True, mininterval=0.5, **kwargs)
