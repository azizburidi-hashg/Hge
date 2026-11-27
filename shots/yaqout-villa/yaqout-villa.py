"""B-roll for the Al-Yaqout villa offer (IMG_4841). Isometric 3D diorama, almost no text: a city rises, a "01" pin drops,
the villa builds itself, three plots pop in beside it, and each plot transforms on its word (court, pool, rest house),
then trees fill the site. Beat times (seconds) come from the voiceover's word timestamps; change them at the top.
  python .claude/skills/blender-shots/scripts/render_blender.py shots/yaqout-villa/yaqout-villa.py --out shots/yaqout-villa/yaqout-villa.mp4 --frames 366 --stills 20,100,170,245,320
"""
import math
import random

import bpy
import blender_kit as kit

a = kit.args()
END = a.frames
F = kit.f

# ---------------------------------------------------------------- beats (seconds into the voiceover)
T_PIN = a.get("pin", 0.55, float)          # "العرض الأول" (the first offer)
T_VILLA = a.get("villa", 2.45, float)      # "فيلا بحي الياقوت" (a villa in Al-Yaqout)
T_PLOTS = (4.55, 5.0, 5.45)                # "مجاورها ثلاث أراضي" (next to it, three plots)
T_READY = 6.05                             # "بإمكانك تخليها" (you can turn them into)
T_COURT = a.get("court", 7.4, float)       # "ملاعب" (courts)
T_POOL = a.get("pool", 7.94, float)        # "مسبح" (pool)
T_REST = a.get("rest", 8.76, float)        # "استراحة" (rest house)
T_MORE = a.get("more", 9.45, float)        # "أو إلى آخره" (and so on)

SAND, LOT, ASPHALT = "#D9C59C", "#CDBB97", "#2B313B"
WHITE, WOOD, GLASS = "#F3EFE7", "#8A5A3A", "#24384F"
ACCENT, GREEN, WATER, CLAY = "#E0A040", "#3E9E4F", "#38B2EE", "#B5562F"

kit.setup(world="#1A2230", look="Medium High Contrast", motion_blur=0, bloom=0)   # no blur: halves render time on this slow PC
random.seed(4)


# ---------------------------------------------------------------- helpers
def box(name, size, loc, mat, par=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    kit.assign(ob, mat)
    if par:
        kit.parent(ob, par)
        ob.location = loc
    return ob


def cyl(name, r, h, loc, mat, par=None, verts=16):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, vertices=verts)
    ob = bpy.context.object
    ob.name = name
    kit.assign(ob, mat)
    if par:
        kit.parent(ob, par)
        ob.location = loc
    return ob


def group(name, loc):
    g = kit.empty(loc, name)
    g.scale = (0.001, 0.001, 0.001)
    return g


def pop(ob, t, dur=0.35, ease="back", full=(1, 1, 1)):
    """Scale from nothing to full, with overshoot."""
    tiny = tuple(max(0.001, v * 0.001) for v in full)
    kit.key(ob, "scale", [(F(t), tiny, ease), (F(t + dur), full)])


def rise(ob, t, dur=0.4, ease="expo"):
    """Grow up out of the ground (Z only)."""
    ob.scale = (0.001, 0.001, 0.001)
    kit.key(ob, "scale", [(max(1, F(t) - 1), (0.001, 0.001, 0.001), "hold"), (F(t), (1, 1, 0.001), ease),
                          (F(t + dur), (1, 1, 1))])


def appear(ob, t):
    """Invisible until just before t (for things that drop in from above)."""
    ob.scale = (0.001, 0.001, 0.001)
    kit.key(ob, "scale", [(1, (0.001, 0.001, 0.001), "hold"), (max(2, F(t) - 1), (1, 1, 1))])


def glow(mat, keys):
    node = next(n for n in mat.node_tree.nodes if n.type == "EMISSION")
    kit.key(node.inputs["Strength"], "default_value", [(F(t), v) for t, v in keys])


def palm(name, loc, h=1.7):
    g = group(name, loc)
    cyl(name + "_trunk", 0.07, h, (0, 0, h / 2), trunk_mat, g, 8)
    for i in range(6):
        ang = i * 60
        fr = box(f"{name}_frond{i}", (0.85, 0.2, 0.04), (0, 0, h), leaf_mat, g)
        fr.rotation_euler = kit.rot(0, -22, ang)
        fr.location = (0.38 * math.cos(math.radians(ang)), 0.38 * math.sin(math.radians(ang)), h - 0.08)
    return g


trunk_mat = kit.matte("#7A5536", 0.8, "Trunk")
leaf_mat = kit.matte("#4E8F3A", 0.6, "Leaf")

# ---------------------------------------------------------------- the ground and the city that rises around the site
kit.floor(ASPHALT, z=0.0, size=260, roughness=0.9, name="Ground")
box("Lot", (16.5, 8.2, 0.06), (2.2, 0.0, 0.03), kit.matte(LOT, 0.9, "LotMat"))
SITE = (-6.5, 11.0, -4.8, 4.8)                       # x0, x1, y0, y1 kept clear of city blocks
block_mats = [kit.matte(c, 0.7, f"Block{i}") for i, c in enumerate(("#C9CDD3", "#B9C0C9", "#D8D3C8", "#AEB6C1"))]
blocks = []
for gx in range(-8, 9):
    for gy in range(-6, 7):
        x, y = gx * 4.4 + 2.2, gy * 4.4
        if SITE[0] - 1 < x < SITE[1] + 1 and SITE[2] - 1 < y < SITE[3] + 1:
            continue
        if random.random() < 0.22:
            continue
        w, d, h = random.uniform(2.2, 3.4), random.uniform(2.2, 3.4), random.choice((0.8, 1.2, 1.6, 2.4, 3.2))
        root = kit.empty((x, y, 0.0), f"B{gx}_{gy}")
        box(f"B{gx}_{gy}_m", (w, d, h), (0, 0, h / 2), random.choice(block_mats), root)
        dist = math.hypot(x - 2.2, y)
        rise(root, 0.02 + min(dist, 40) / 40 * 0.75, dur=0.45)

# ---------------------------------------------------------------- the "01" pin: drops on the lot, pulses, then hovers over the villa
VX = -3.6
pin = kit.empty((VX, 0, 14), "Pin")
pin_mat = kit.matte("#E9A83A", 0.35, "PinGold")
bpy.ops.mesh.primitive_cone_add(radius1=0.55, radius2=0.0, depth=1.6, location=(0, 0, 0.8), vertices=24)
cone = bpy.context.object
cone.rotation_euler = kit.rot(180, 0, 0)
kit.assign(cone, pin_mat)
kit.parent(cone, pin)
cone.location = (0, 0, 0.8)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.95, location=(0, 0, 2.2), segments=32, ring_count=16)
head = bpy.context.object
kit.assign(head, pin_mat)
kit.parent(head, pin)
head.location = (0, 0, 2.2)
for p in head.data.polygons:
    p.use_smooth = True
badge = kit.text("01", font="Anton-Regular", size=1.05, color="#10141B", strength=1.0, loc=(0, 0, 2.2), rot=(90, 0, -45), name="Badge")
kit.parent(badge, pin)
badge.location = (-0.7, -0.7, 2.12)          # on the head's surface, toward the camera (azimuth 225)
pin.scale = (2.2, 2.2, 2.2)
kit.key(pin, "location", [(1, (VX, 0, 24)), (F(T_PIN), (VX, 0, 24), "bounce"), (F(T_PIN + 0.55), (VX, 0, 0.06)),
                          (F(T_VILLA - 0.05), (VX, 0, 0.06), "back"), (F(T_VILLA + 0.45), (VX, 0, 3.7), "in_out"),
                          (END, (VX, 0, 4.0))])
kit.key(pin, "scale", [(F(T_VILLA - 0.05), (2.2, 2.2, 2.2), "back"), (F(T_VILLA + 0.45), (0.85, 0.85, 0.85))])
kit.key(pin, "rotation_euler", [(F(T_VILLA + 0.5), kit.rot(0, 0, 0), "linear"), (END, kit.rot(0, 0, 40))])

bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.06, location=(VX, 0, 0.1), major_segments=64, minor_segments=8)
ring = bpy.context.object
ring.name = "PulseRing"
ring_mat = kit.emission(ACCENT, 4.0, "Ring")
kit.assign(ring, ring_mat)
tp = T_PIN + 0.55
kit.key(ring, "scale", [(F(tp), (0.3, 0.3, 1), "out"), (F(tp + 0.8), (6, 6, 1))])
kit.fade(ring, [(F(tp) - 1, 0.0), (F(tp), 1.0), (F(tp + 0.8), 0.0)])

# ---------------------------------------------------------------- the villa builds itself
villa_white = kit.matte(WHITE, 0.55, "VillaWhite")
villa_wood = kit.matte(WOOD, 0.6, "VillaWood")
win_mat = kit.emission("#FFD89A", 0.0, "Windows")
glow(win_mat, [(T_VILLA + 0.85, 0.12), (T_VILLA + 1.1, 4.0), (T_VILLA + 1.3, 2.2)])
ground_floor = kit.empty((VX, 0, 0.06), "GroundFloor")
box("GF", (3.4, 3.0, 1.5), (0, 0, 0.75), villa_white, ground_floor)
box("GFdoor", (0.7, 0.05, 1.1), (0.4, -1.52, 0.55), villa_wood, ground_floor)
for x in (-1.1, 1.25):
    box(f"GFwin{x}", (0.7, 0.05, 0.6), (x, -1.52, 0.85), win_mat, ground_floor)
for y in (-0.6, 0.7):
    box(f"GFwinS{y}", (0.05, 0.7, 0.6), (-1.72, y, 0.85), win_mat, ground_floor)
rise(ground_floor, T_VILLA + 0.1, dur=0.35)

upper = kit.empty((VX - 0.3, 0.3, 1.56), "Upper")
box("UF", (2.6, 2.3, 1.25), (0, 0, 0.62), villa_white, upper)
box("UFslat", (1.3, 0.05, 0.75), (0.3, -1.17, 0.65), villa_wood, upper)
box("UFwin", (0.6, 0.05, 0.6), (-0.7, -1.17, 0.7), win_mat, upper)
box("UFwinS", (0.05, 1.0, 0.6), (-1.32, 0.0, 0.7), win_mat, upper)
box("Parapet", (2.8, 2.5, 0.12), (0, 0, 1.31), villa_white, upper)
appear(upper, T_VILLA + 0.4)
kit.key(upper, "location", [(1, (VX - 0.3, 0.3, 8)), (F(T_VILLA + 0.4), (VX - 0.3, 0.3, 8), "bounce"),
                            (F(T_VILLA + 0.85), (VX - 0.3, 0.3, 1.56))])
canopy = box("Canopy", (1.6, 1.1, 0.08), (VX + 0.9, -1.9, 1.5), villa_wood)
pop(canopy, T_VILLA + 0.75, 0.3, full=(1.6, 1.1, 0.08))
for i, (x, y) in enumerate(((VX - 2.3, -1.9), (VX + 2.2, 1.9), (VX - 2.2, 2.0))):
    pop(palm(f"VPalm{i}", (x, y, 0.06)), T_VILLA + 1.0 + i * 0.1, 0.4)

# ---------------------------------------------------------------- three plots pop in beside the villa, one per beat
PX = (0.6, 4.2, 7.8)
PW, PD = 3.1, 3.6
plot_roots, outline_mats = [], []
for i, (x, t) in enumerate(zip(PX, T_PLOTS)):
    root = kit.empty((x, 0, 0.06), f"Plot{i}")
    box(f"Plot{i}_soil", (PW, PD, 0.12), (0, 0, 0.06), kit.matte(SAND, 0.95, f"Soil{i}"), root)
    om = kit.emission(ACCENT, 2.0, f"Outline{i}")
    outline_mats.append(om)
    for j, (sx, sy, lx, ly) in enumerate(((PW, 0.07, 0, -PD / 2), (PW, 0.07, 0, PD / 2),
                                          (0.07, PD, -PW / 2, 0), (0.07, PD, PW / 2, 0))):
        box(f"Plot{i}_edge{j}", (sx, sy, 0.05), (lx, ly, 0.14), om, root)
    for j, (cx, cy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        cyl(f"Plot{i}_stake{j}", 0.06, 0.45, (cx * PW / 2, cy * PD / 2, 0.22), om, root, 8)
    pop(root, t, 0.4)
    plot_roots.append(root)

# "you can turn them into": a glow sweeps across the plots and each one lifts a little, ready to change
for i, (root, om) in enumerate(zip(plot_roots, outline_mats)):
    t = T_READY + i * 0.22
    glow(om, [(t - 0.05, 2.0), (t + 0.15, 9.0), (t + 0.55, 2.5)])
    kit.key(root, "location", [(F(t), (PX[i], 0, 0.06), "out"), (F(t + 0.25), (PX[i], 0, 0.3), "in_out"),
                               (F(t + 0.6), (PX[i], 0, 0.06))])
# each outline dims once its plot has transformed
for om, t in zip(outline_mats, (T_COURT, T_POOL, T_REST)):
    glow(om, [(t + 0.3, 2.5), (t + 0.7, 0.6)])

# ---------------------------------------------------------------- plot 1 -> sports court
court = kit.empty((PX[0], 0, 0.18), "Court")
box("CourtTurf", (PW - 0.3, PD - 0.3, 0.08), (0, 0, 0.04), kit.matte(GREEN, 0.7, "Turf"), court)
line = kit.emission("#FFFFFF", 1.6, "CourtLines")
for j, (sx, sy, lx, ly) in enumerate(((PW - 0.6, 0.05, 0, -(PD - 0.6) / 2), (PW - 0.6, 0.05, 0, (PD - 0.6) / 2),
                                      (0.05, PD - 0.6, -(PW - 0.6) / 2, 0), (0.05, PD - 0.6, (PW - 0.6) / 2, 0),
                                      (PW - 0.6, 0.05, 0, 0))):
    box(f"CourtLine{j}", (sx, sy, 0.02), (lx, ly, 0.09), line, court)
bpy.ops.mesh.primitive_torus_add(major_radius=0.45, minor_radius=0.025, location=(0, 0, 0.09), major_segments=48, minor_segments=6)
circ = bpy.context.object
kit.assign(circ, line)
kit.parent(circ, court)
circ.location = (0, 0, 0.09)
goal_mat = kit.matte("#F5F5F5", 0.4, "Goal")
for s in (-1, 1):
    g = kit.empty((PX[0], s * (PD / 2 - 0.35), 0.26), f"Goal{s}")
    for gx in (-0.45, 0.45):
        box(f"Goal{s}_post{gx}", (0.06, 0.06, 0.6), (gx, 0, 0.3), goal_mat, g)
    box(f"Goal{s}_bar", (0.96, 0.06, 0.06), (0, 0, 0.6), goal_mat, g)
    pop(g, T_COURT + 0.25 + (s + 1) * 0.04, 0.3)
pop(court, T_COURT, 0.35, ease="back")
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(PX[0], 0, 2.5), segments=16, ring_count=8)
ball = bpy.context.object
kit.assign(ball, kit.matte("#FFFFFF", 0.4, "Ball"))
appear(ball, T_COURT + 0.35)
kit.key(ball, "location", [(1, (PX[0] + 0.3, -0.4, 6)), (F(T_COURT + 0.35), (PX[0] + 0.3, -0.4, 6), "bounce"),
                           (F(T_COURT + 0.95), (PX[0] + 0.3, -0.4, 0.4))])

# ---------------------------------------------------------------- plot 2 -> swimming pool
pool = kit.empty((PX[1], 0, 0.18), "Pool")
deck = kit.matte("#ECE6DA", 0.6, "Deck")
for j, (sx, sy, lx, ly) in enumerate(((PW - 0.3, 0.45, 0, -(PD - 0.75) / 2), (PW - 0.3, 0.45, 0, (PD - 0.75) / 2),
                                      (0.45, PD - 0.3, -(PW - 0.75) / 2, 0), (0.45, PD - 0.3, (PW - 0.75) / 2, 0))):
    box(f"Coping{j}", (sx, sy, 0.16), (lx, ly, 0.08), deck, pool)
pop(pool, T_POOL - 0.05, 0.3)
water_root = kit.empty((PX[1], 0, 0.18), "WaterRoot")
water_mat = kit.emission(WATER, 0.0, "Water")
glow(water_mat, [(T_POOL + 0.1, 0.4), (T_POOL + 0.35, 1.6), (T_POOL + 0.6, 1.1)])
box("Water", (PW - 1.2, PD - 1.2, 0.12), (0, 0, 0.06), water_mat, water_root)
rise(water_root, T_POOL + 0.1, 0.35, ease="out")
lounger = kit.matte("#FFFFFF", 0.5, "Lounger")
for k, y in enumerate((-0.5, 0.4)):
    lg = kit.empty((PX[1] + PW / 2 + 0.45, y, 0.06), f"Lounger{k}")
    box(f"Lounger{k}_m", (0.4, 0.75, 0.12), (0, 0, 0.12), lounger, lg)
    pop(lg, T_POOL + 0.4 + k * 0.08, 0.3)

# ---------------------------------------------------------------- plot 3 -> rest house (istiraha): canopy, rug, cushions, fire pit
rest = kit.empty((PX[2], 0, 0.18), "Rest")
rug = kit.empty((PX[2], 0, 0.18), "RugRoot")
box("Rug", (PW - 0.8, PD - 1.0, 0.04), (0, 0, 0.02), kit.matte("#9E2F2F", 0.8, "RugMat"), rug)
pop(rug, T_REST - 0.1, 0.3)
cush = kit.matte("#E8D9B5", 0.7, "Cushion")
for k, (cx, cy, sx, sy) in enumerate(((0, 1.05, 1.9, 0.35), (-0.95, 0, 0.35, 1.7), (0.95, 0, 0.35, 1.7))):
    cg = kit.empty((PX[2] + cx, cy, 0.22), f"Cush{k}")
    box(f"Cush{k}_m", (sx, sy, 0.22), (0, 0, 0.11), cush, cg)
    pop(cg, T_REST + 0.05 + k * 0.06, 0.28)
post_mat = kit.matte(WOOD, 0.6, "Posts")
for k, (cx, cy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
    pg = kit.empty((PX[2] + cx * 1.2, cy * 1.4, 0.18), f"Post{k}")
    cyl(f"Post{k}_m", 0.06, 1.5, (0, 0, 0.75), post_mat, pg, 8)
    rise(pg, T_REST - 0.05 + k * 0.04, 0.3)
roof_root = kit.empty((PX[2], 0, 1.68), "RoofRoot")
bpy.ops.mesh.primitive_cone_add(radius1=2.05, radius2=0.0, depth=0.9, location=(0, 0, 0.45), vertices=4)
roof = bpy.context.object
roof.name = "Roof"
roof.scale = (1.0, 1.17, 1.0)
roof.rotation_euler = kit.rot(0, 0, 45)
kit.assign(roof, kit.matte(CLAY, 0.7, "RoofMat"))
kit.parent(roof, roof_root)
roof.location = (0, 0, 0.45)
appear(roof_root, T_REST + 0.2)
kit.key(roof_root, "location", [(1, (PX[2], 0, 9)), (F(T_REST + 0.2), (PX[2], 0, 9), "bounce"), (F(T_REST + 0.65), (PX[2], 0, 1.68))])
fire_mat = kit.emission("#FF8A2A", 0.0, "Fire")
glow(fire_mat, [(T_REST + 0.5, 0.5), (T_REST + 0.7, 7.0), (T_REST + 0.9, 4.5)])
fire = cyl("FirePit", 0.28, 0.1, (PX[2], -0.1, 0.27), fire_mat, None, 16)
pop(fire, T_REST + 0.45, 0.25, full=(1, 1, 1))
pop(palm("RestPalm", (PX[2] + PW / 2 + 0.35, 1.5, 0.06), 1.9), T_REST + 0.6, 0.4)

# ---------------------------------------------------------------- "and so on": trees sprout along the whole site
for i, x in enumerate((-5.4, -1.2, 2.4, 6.0, 9.6)):
    pop(palm(f"Row{i}", (x, -3.75, 0.06), random.uniform(1.1, 1.35)), T_MORE + i * 0.1, 0.35)
for i, x in enumerate((-5.2, -1.6, 0.6, 2.4, 4.2, 6.0, 9.8)):
    pop(palm(f"Back{i}", (x, 3.5, 0.06), random.uniform(1.5, 2.0)), T_MORE + 0.15 + i * 0.08, 0.35)

# ---------------------------------------------------------------- light: one warm sun, a cool fill from the sky colour
sun = kit.light("SUN", (-14, -22, 30), (2, 0, 0), power=3.2, color="#FFE9CF", name="Sun")
sun.data.angle = math.radians(1)
fill = kit.light("AREA", (24, -10, 18), (2, 0, 0), power=9000, color="#A9C3FF", size=3.0, name="Fill")
fill.data.use_shadow = False
for lt in bpy.data.lights:
    if hasattr(lt, "use_shadow_jitter"):
        lt.use_shadow_jitter = False

# ---------------------------------------------------------------- camera: isometric from the front-left; wide city -> villa -> villa + plots
el, az, dist = math.radians(34), math.radians(225), 60.0
off = (dist * math.cos(el) * math.cos(az), dist * math.cos(el) * math.sin(az), dist * math.sin(el))
shots = [  # (seconds, look-at, ortho width, ease into the next key)
    (0.0, (1.5, 0, 0), 50, "in_out"),
    (T_VILLA - 0.2, (-0.5, 0, 0), 42, "expo"),
    (T_VILLA + 0.5, (VX + 0.2, 0, 2.2), 14.0, "in_out"),
    (3.95, (VX + 0.5, 0, 2.1), 13.3, "expo"),
    (4.7, (2.5, 0, 0.6), 22.0, "in_out"),
    (T_COURT - 0.1, (2.6, 0, 0.6), 21.0, "in_out"),
    (T_REST + 0.5, (2.8, 0, 0.6), 19.5, "in_out"),
    (T_MORE + 1.0, (2.2, 0, 0.6), 23.5, "in_out"),
    (END / a.fps, (2.2, 0, 0.6), 22.8, "in_out"),
]
cam = kit.camera(tuple(shots[0][1][i] + off[i] for i in range(3)), look_at=shots[0][1], lens=50, ortho=shots[0][2])
cam.data.clip_end = 300
kit.key(cam, "location", [(F(t), tuple(p[i] + off[i] for i in range(3)), e) for t, p, _, e in shots])
kit.key(kit.aim(cam), "location", [(F(t), p, e) for t, p, _, e in shots])
kit.key(cam.data, "ortho_scale", [(F(t), o, e) for t, _, o, e in shots])

kit.post(bloom=0, vignette=0.3, grain=0)   # light finish: keeps the render under the time limit
