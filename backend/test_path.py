import os
base = os.path.join(os.path.dirname(__file__), '../frontend/dist')
print("Sökväg till React-build:", base)
print("Finns index.html?", os.path.exists(os.path.join(base, "index.html")))