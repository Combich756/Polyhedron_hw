#!/usr/bin/env -S python3 -B

from time import time
from common.tk_drawer import TkDrawer
from shadow.polyedr import Polyedr


tk = TkDrawer()
try:
    for name in ["ccc", "cube", "box", "king", "cow"]:
        print("=============================================================")
        print(f"Начало работы с полиэдром '{name}'")
        polyedr = Polyedr(f"data/{name}.geom")
        print(
            "Сумма длин проекций полностью невидимых рёбер "
            "с дополнительными условиями:",
            polyedr.hidden_edge_projection_sum(),
        )
        start_time = time()
        polyedr.draw(tk)
        delta_time = time() - start_time
        print(f"Изображение полиэдра '{name}' заняло {delta_time} сек.")
        input("Hit 'Return' to continue -> ")
except (EOFError, KeyboardInterrupt):
    print("\nStop")
    tk.close()
