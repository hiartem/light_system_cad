# Parametric ESP32-S3 case – run inside FreeCAD (Macro → Macros… → Execute), or from the Python console:
#   p = "/path/to/esp32s3_case.py"; exec(open(p).read(), {"__file__": p})
# Output (.FCStd + STLs) is written next to this script.
# All dimensions in mm. Values marked "verify" are typical figures – measure your parts.
import FreeCAD as App, Part, math, os
from FreeCAD import Vector as V

DOC = "ESP32S3_Case"

def _script_dir():
    f = globals().get("__file__")
    if f and os.path.basename(f) == "esp32s3_case.py":
        return os.path.dirname(os.path.abspath(f))
    # exec() without __file__: fall back to where the open document was saved
    if DOC in App.listDocuments() and App.getDocument(DOC).FileName:
        return os.path.dirname(App.getDocument(DOC).FileName)
    raise RuntimeError('Cannot locate script folder – run with exec(open(p).read(), {"__file__": p})')

OUT = os.path.join(_script_dir(), DOC)
X, Y = V(1, 0, 0), V(0, 1, 0)

# ---------------- Components ----------------
bL, bW, bT = 69.0, 25.4, 1.6                       # ESP32-S3-DevKitC-1
dL, dW, dT   = 44.5, 37.0, 1.6                     # OLED 1.54" 128x64 7-pin – verify
gL, gW, gT   = 42.04, 27.22, 1.4
aL, aW       = 35.05, 17.52
a_off_y      = 2.0
d_hole_dx, d_hole_dy, d_hole_d = 39.5, 32.0, 2.5
win_m = 0.6
eL, eW, eH   = 13.2, 12.4, 6.5                     # Bourns PEC11R-4115F-S0018 – verify
e_bush_d, e_bush_h = 9.0, 7.0
e_shaft_d, e_shaft_len, e_flat = 6.0, 15.0, 4.5
e_hole_d = 9.5
pL, pW, pT, pH = 43.2, 21.0, 1.6, 14.0             # LM2596S-5V module – verify
p_holes = [(4.0, 3.0), (pL - 4.0, pW - 3.0)]
p_stand_h, p_stand_d, p_pilot_d = 3.0, 6.0, 2.5
j_thread_d, j_collar_l, j_len, j_lug_l = 8.0, 3.8, 12.0, 18.0   # DC jack 5.5x2.1 M8x1
j_collar_d, j_nut_d = 10.5, 11.5                   # verify
j_hole_d = 8.3
s_cut_w, s_cut_h = 9.2, 14.2                       # SMRS-101-1 rocker cutout (Y x Z)
s_bez_w, s_bez_h, s_bez_t = 11.0, 16.0, 2.5        # verify
s_depth, s_lug_l = 11.5, 6.5
pe_z, j_y_off, s_y_off = 17.0, -6.0, +7.0          # power entry on +X end wall
# IRFR120N (FR120N) MOSFET module x2 – verify
mL, mW, mT, mH = 34.0, 16.0, 1.6, 11.5             # mH = total height incl. screw terminals
m_holes = [(3.0, mW/2), (mL - 3.0, mW/2)]          # Ø3 holes (module coords: along L, along W)
m_stand_h, m_stand_d, m_pilot_d = 3.0, 6.0, 2.5
m_x0 = 12.0                                        # module start X (output terminals at +X end, toward XT60)
# Amass XT60E-F panel-mount female, one per MOSFET, high on each long wall above the LM2596 – verify
# Mounted externally: flange on the outside of the wall, rear body passes through the wall cutout
xt_fl_w, xt_fl_h, xt_fl_t = 34.0, 15.8, 2.4        # flange (outside the wall)
xt_fr_w, xt_fr_h, xt_fr_d = 16.0, 8.4, 3.3         # socket face protruding in front of the flange
xt_body_w, xt_body_h, xt_body_d = 20.0, 12.0, 14.5 # rear body + solder cups behind flange (goes through wall)
xt_hole_dx, xt_hole_d = 27.0, 3.2                  # flange holes (M3 screw + nut)
xt_cut_clr = 0.3
xt_cx, xt_z0 = 90.0, 20.0                          # centre X, flange bottom Z

# ---------------- Case ----------------
clr, wall, floor_t = 0.6, 2.0, 2.0
under, over = 11.0, 22.0
lid_t = 2.5
lip_h, lip_t, g = 2.0, 1.2, 0.2
boss_d, pilot_d, pilot_depth = 7.0, 2.6, 12.0
scr_d, csk_d = 3.4, 6.6
end_zone = 42.0
side_strip = mW + 1.4                              # free strip each side of ESP board for MOSFET modules
# Keyholes (wall mount)
kh_head_d, kh_slot_w, kh_slot_l, kh_head_h, kh_cap, kh_wall = 8.5, 4.2, 8.0, 3.2, 1.2, 1.5
kh_dir, kh_inset = +1, 12.0                        # slot toward +Y (= up on wall)
# Knob
k_d, k_h, k_gap, rec_d, rec_h = 20.0, 14.0, 0.8, 15.0, 5.0
bore_d, bore_flat = 6.15, 4.65
n_flutes, flute_d, chamfer = 24, 1.6, 1.2
explode = 30

# ---------------- Derived ----------------
iL = bL + 2*clr + end_zone
iW = max(bW + 2*side_strip, dW + 2*(g + lip_t) + 1.0, pL + 1.6) + 2*clr
oL, oW = iL + 2*wall, iW + 2*wall
board_x = wall + clr
board_y = (oW - bW)/2
board_z = floor_t + under
base_h  = board_z + bT + over
bo = wall + boss_d/2 - 0.5
boss_pts = [(bo, bo), (oL-bo, bo), (bo, oW-bo), (oL-bo, oW-bo)]
p_x, p_y, p_z = board_x + bL + clr + 0.8, (oW - pL)/2, floor_t + p_stand_h
p_hole_pts = [(p_x + pW - v, p_y + u) for (u, v) in p_holes]
j_y, s_y = oW/2 + j_y_off, oW/2 + s_y_off
m_y = [wall + 0.7, oW - wall - 0.7 - mW]           # the two MOSFET modules (low-Y, high-Y)
m_z = floor_t + m_stand_h
m_hole_pts = [(m_x0 + u, y + v) for y in m_y for (u, v) in m_holes]
kh_pts = [(kh_inset, oW/2 - kh_dir*kh_slot_l/2), (oL - kh_inset, oW/2 - kh_dir*kh_slot_l/2)]

# ================= BASE =================
base = Part.makeBox(oL, oW, base_h)
base = base.cut(Part.makeBox(iL, iW, base_h, V(wall, wall, floor_t)))
sup_w = 4.0
for x in (wall, board_x + bL - sup_w + clr):       # end supports only under the board (+3 mm guides)
    base = base.fuse(Part.makeBox(sup_w, bW + 6.0, under, V(x, board_y - 3.0, floor_t)))
    for y0 in (board_y - 3.0, board_y + bW + 0.3):
        base = base.fuse(Part.makeBox(sup_w, 2.7, under + bT + 1.5, V(x, y0, floor_t)))
for (x, y) in boss_pts:
    base = base.fuse(Part.makeCylinder(boss_d/2, base_h - floor_t, V(x, y, floor_t)))
for (x, y) in p_hole_pts:
    base = base.fuse(Part.makeCylinder(p_stand_d/2, p_stand_h, V(x, y, floor_t)))
for (x, y) in m_hole_pts:
    base = base.fuse(Part.makeCylinder(m_stand_d/2, m_stand_h, V(x, y, floor_t)))
# keyhole pads
pad_w, pad_l, pad_h = kh_head_d + 2*kh_wall, kh_slot_l + kh_head_d + 2*kh_wall, kh_head_h + kh_cap
for (x, y) in kh_pts:
    y_lo = min(y, y + kh_dir*kh_slot_l) - kh_head_d/2 - kh_wall
    base = base.fuse(Part.makeBox(pad_w, pad_l, pad_h, V(x - pad_w/2, y_lo, floor_t)))
# --- cuts ---
for (x, y) in boss_pts:
    base = base.cut(Part.makeCylinder(pilot_d/2, pilot_depth + 0.01, V(x, y, base_h - pilot_depth)))
for (x, y) in p_hole_pts + m_hole_pts:
    base = base.cut(Part.makeCylinder(p_pilot_d/2, p_stand_h + 1.0, V(x, y, floor_t - 1.0 + 0.01)))
# Two shaped USB-C openings (stadium) in the -X end wall, one per board port
usb_dy  = [-6.0, +6.0]          # port centres from board centre line – verify on your board
usb_zc  = board_z + bT + 1.63   # receptacle centre (3.26 mm tall, top-mounted)
usb_w, usb_h, usb_r = 10.5, 5.0, 2.5
for dy in usb_dy:
    yc = board_y + bW/2 + dy
    slot = Part.makeBox(wall + 1, usb_w - 2*usb_r, usb_h, V(-0.5, yc - usb_w/2 + usb_r, usb_zc - usb_h/2))
    for ey in (yc - usb_w/2 + usb_r, yc + usb_w/2 - usb_r):
        slot = slot.fuse(Part.makeCylinder(usb_r, wall + 1, V(-0.5, ey, usb_zc), X))
    base = base.cut(slot)
vent_x = [wall + 18 + i*6 for i in range(8)] + [p_x + 3 + i*6 for i in range(3)]
for x in vent_x:
    for y in (-0.5, oW - wall - 0.5):
        base = base.cut(Part.makeBox(2.0, wall + 1, 10.0, V(x, y, floor_t + 4)))
base = base.cut(Part.makeCylinder(j_hole_d/2, wall + 2, V(oL - wall - 1, j_y, pe_z), X))
base = base.cut(Part.makeBox(wall + 2, s_cut_w, s_cut_h, V(oL - wall - 1, s_y - s_cut_w/2, pe_z - s_cut_h/2)))
# XT60E-F outputs on both long walls (external mount): rear-body cutout + 2 screw holes
xt_zc = xt_z0 + xt_fl_h/2
for y in (-0.5, oW - wall - 0.5):
    base = base.cut(Part.makeBox(xt_body_w + 2*xt_cut_clr, wall + 1, xt_body_h + 2*xt_cut_clr,
                                 V(xt_cx - xt_body_w/2 - xt_cut_clr, y, xt_zc - xt_body_h/2 - xt_cut_clr)))
    for sx in (-1, 1):
        base = base.cut(Part.makeCylinder(xt_hole_d/2, wall + 1, V(xt_cx + sx*xt_hole_dx/2, y, xt_zc), Y))
for (x, y) in ((8, 8), (oL-8, 8), (8, oW-8), (oL-8, oW-8)):
    base = base.cut(Part.makeCylinder(4.0, 0.8, V(x, y, -0.01)))
for (x, y) in kh_pts:
    y2 = y + kh_dir*kh_slot_l
    ymin, ymax = min(y, y2), max(y, y2)
    base = base.cut(Part.makeCylinder(kh_head_d/2, floor_t + pad_h + 1, V(x, y, -0.5)))
    base = base.cut(Part.makeBox(kh_slot_w, ymax - ymin, floor_t + 1, V(x - kh_slot_w/2, ymin, -0.5)))
    base = base.cut(Part.makeCylinder(kh_slot_w/2, floor_t + 1, V(x, y2, -0.5)))
    base = base.cut(Part.makeBox(kh_head_d, ymax - ymin, kh_head_h, V(x - kh_head_d/2, ymin, floor_t)))
    base = base.cut(Part.makeCylinder(kh_head_d/2, kh_head_h, V(x, y2, floor_t)))
base = base.removeSplitter()
if not base.isValid():
    base.fix(0.01, 0.01, 0.01)

# ================= LID (local z=0 = underside) =================
d_x = board_x + 26.0
d_y = (oW - dW)/2
d_cx, d_cy = d_x + dL/2, d_y + dW/2
pcb_top_z = -gT
e_cx, e_cy = d_x + dL + 9.1, oW/2

lid = Part.makeBox(oL, oW, lid_t)
lip = Part.makeBox(iL - 2*g, iW - 2*g, lip_h, V(wall + g, wall + g, -lip_h))
lip = lip.cut(Part.makeBox(iL - 2*g - 2*lip_t, iW - 2*g - 2*lip_t, lip_h, V(wall + g + lip_t, wall + g + lip_t, -lip_h)))
for (x, y) in boss_pts:
    lip = lip.cut(Part.makeCylinder(boss_d/2 + 0.4, lip_h + 0.2, V(x, y, -lip_h - 0.1)))
lid = lid.fuse(lip)
holes = [(d_cx + sx*d_hole_dx/2, d_cy + sy*d_hole_dy/2) for sx in (-1, 1) for sy in (-1, 1)]
for (x, y) in holes:
    lid = lid.fuse(Part.makeCylinder(2.5, gT, V(x, y, -gT)))
lid = lid.cut(Part.makeBox(gL + 0.4, gW + 0.4, 0.5 + gT + 0.01, V(d_cx - (gL+0.4)/2, d_cy - (gW+0.4)/2, -gT - 0.01)))
wL, wW = aL + 2*win_m, aW + 2*win_m
wcy = d_cy + a_off_y
inner = Part.makePlane(wL, wW, V(d_cx - wL/2, wcy - wW/2, 0.5))
outer = Part.makePlane(wL + 2*(lid_t-0.5), wW + 2*(lid_t-0.5),
                       V(d_cx - wL/2 - (lid_t-0.5), wcy - wW/2 - (lid_t-0.5), lid_t + 0.001))
lid = lid.cut(Part.makeLoft([inner.OuterWire, outer.OuterWire], True))
lid = lid.cut(Part.makeBox(wL, wW, 1.0, V(d_cx - wL/2, wcy - wW/2, -0.2)))
for (x, y) in holes:
    lid = lid.cut(Part.makeCylinder(0.9, gT + lid_t - 0.6, V(x, y, -gT - 0.01)))
lid = lid.cut(Part.makeCylinder(e_hole_d/2, lid_t + 4, V(e_cx, e_cy, -2)))
csk_h = (csk_d - scr_d) / 2
for (x, y) in boss_pts:
    lid = lid.cut(Part.makeCylinder(scr_d/2, lid_t + 2, V(x, y, -1)))
    lid = lid.cut(Part.makeCone(scr_d/2, csk_d/2, csk_h + 0.01, V(x, y, lid_t - csk_h)))
for (x, y, r) in ((board_x + 5.5, board_y + 3.5, 1.6), (board_x + 5.5, board_y + bW - 3.5, 1.6),
                  (board_x + 12.0, board_y + bW/2, 1.5)):
    lid = lid.cut(Part.makeCylinder(r, lid_t + 2, V(x, y, -1)))
for i in range(3):
    lid = lid.cut(Part.makeBox(1.8, 18.0, lid_t + 2, V(board_x + 15.5 + i*3.2, (oW - 18)/2, -1)))
lid = lid.removeSplitter()

# ================= KNOB (local z=0 = knob bottom) =================
bore_h = (e_shaft_len - lid_t) - k_gap + 0.3
knob = Part.makeCylinder(k_d/2, k_h - chamfer).fuse(
       Part.makeCone(k_d/2, k_d/2 - chamfer, chamfer, V(0, 0, k_h - chamfer)))
for i in range(n_flutes):
    a = 2*math.pi*i/n_flutes
    knob = knob.cut(Part.makeCylinder(flute_d/2, k_h - chamfer - 1.5,
                    V((k_d/2 + 0.35)*math.cos(a), (k_d/2 + 0.35)*math.sin(a), 0)))
knob = knob.cut(Part.makeCylinder(rec_d/2, rec_h, V(0, 0, -0.01)))
bore = Part.makeCylinder(bore_d/2, bore_h, V(0, 0, -0.01))
bore = bore.cut(Part.makeBox(bore_d, bore_d, bore_h + 1, V(bore_flat - bore_d/2, -bore_d/2, -0.5)))
knob = knob.cut(bore)
knob = knob.cut(Part.makeBox(k_d/2 - chamfer - 1.5, 1.2, 0.8, V(1.5, -0.6, k_h - 0.8)))
knob = knob.removeSplitter()

# ================= REFERENCE PARTS =================
pcb = Part.makeBox(bL, bW, bT, V(board_x, board_y, board_z))
module = Part.makeBox(18, 18, 3.2, V(board_x + bL - 25.5, board_y + 3.7, board_z + bT))
usb1 = Part.makeBox(7.5, 9.0, 3.2, V(board_x - 1.0, board_y + bW/2 - 10.5, board_z + bT))
usb2 = Part.makeBox(7.5, 9.0, 3.2, V(board_x - 1.0, board_y + bW/2 + 1.5, board_z + bT))
hdr = [Part.makeBox(22*2.54, 2.54, 8.5, V(board_x + 7.0, y, board_z - 8.5)) for y in (board_y, board_y + bW - 2.54)]
esp = pcb.fuse([module, usb1, usb2] + hdr)

dpcb = Part.makeBox(dL, dW, dT, V(d_x, d_y, pcb_top_z - dT))
for (x, y) in holes:
    dpcb = dpcb.cut(Part.makeCylinder(d_hole_d/2, dT + 1, V(x, y, pcb_top_z - dT - 0.5)))
glass = Part.makeBox(gL, gW, gT, V(d_cx - gL/2, d_cy - gW/2, pcb_top_z))
dhdr = Part.makeBox(7*2.54, 2.54, 8.5, V(d_cx - 7*2.54/2, d_y + dW - 3.5, pcb_top_z - dT - 8.5))
oled = dpcb.fuse([glass, dhdr])

ebody = Part.makeBox(eL, eW, eH, V(e_cx - eL/2, e_cy - eW/2, -eH))
ebush = Part.makeCylinder(e_bush_d/2, e_bush_h, V(e_cx, e_cy, 0))
eshaft = Part.makeCylinder(e_shaft_d/2, e_shaft_len - e_bush_h, V(e_cx, e_cy, e_bush_h))
eshaft = eshaft.cut(Part.makeBox(e_shaft_d, e_shaft_d, 7, V(e_cx - e_shaft_d/2 + e_flat, e_cy - e_shaft_d/2, e_shaft_len - 7)))
epins = [Part.makeBox(0.8, 0.3, 3.5, V(e_cx - 2.5 + i*2.5 - 0.4, e_cy - eW/2 + 0.5, -eH - 3.5)) for i in range(3)] + \
        [Part.makeBox(0.8, 0.3, 3.5, V(e_cx - 2.5 + i*5 - 0.4, e_cy + eW/2 - 0.8, -eH - 3.5)) for i in range(2)]
enc = ebody.fuse([ebush, eshaft] + epins)

ppcb = Part.makeBox(pW, pL, pT, V(p_x, p_y, p_z))
for (x, y) in p_hole_pts:
    ppcb = ppcb.cut(Part.makeCylinder(1.5, pT + 1, V(x, y, p_z - 0.5)))
top = p_z + pT
ind = Part.makeBox(12.5, 12.5, 7.5, V(p_x + (pW - 12.5)/2, p_y + (pL - 12.5)/2, top))
cap1 = Part.makeCylinder(4.0, pH - pT, V(p_x + pW/2, p_y + 7.5, top))
cap2 = Part.makeCylinder(4.0, pH - pT, V(p_x + pW/2, p_y + pL - 7.5, top))
ic = Part.makeBox(9.0, 10.0, 4.5, V(p_x + 1.0, p_y + pL/2 - 5, top)).cut(ind)
pmod = ppcb.fuse([ind, cap1, cap2, ic])

jf = oL + j_collar_l
collar = Part.makeCylinder(j_collar_d/2, j_collar_l, V(oL, j_y, pe_z), X).cut(
         Part.makeCylinder(5.5/2, j_collar_l + 1, V(oL, j_y, pe_z), X))
thread = Part.makeCylinder(j_thread_d/2, j_len - j_collar_l, V(oL - (j_len - j_collar_l), j_y, pe_z), X)
nut = Part.makeCylinder(j_nut_d/2, 2.0, V(oL - wall - 2.0, j_y, pe_z), X).cut(
      Part.makeCylinder(j_thread_d/2, 2.0, V(oL - wall - 2.0, j_y, pe_z), X))
lug1 = Part.makeBox(j_lug_l - j_len, 0.4, 2.5, V(jf - j_lug_l, j_y - 2.7, pe_z - 1.25))
lug2 = Part.makeBox(16.35 - j_len, 0.4, 2.5, V(jf - 16.35, j_y + 2.3, pe_z - 1.25))
djack = collar.fuse([thread, nut, lug1, lug2, Part.makeCylinder(1.0, 6.0, V(jf - 7.0, j_y, pe_z), X)])

bezel = Part.makeBox(s_bez_t, s_bez_w, s_bez_h, V(oL, s_y - s_bez_w/2, pe_z - s_bez_h/2))
rocker = Part.makeBox(1.8, s_bez_w - 2.4, s_bez_h - 2.4, V(oL + s_bez_t, s_y - (s_bez_w - 2.4)/2, pe_z - (s_bez_h - 2.4)/2))
sbody = Part.makeBox(s_depth, 9.0, 13.9, V(oL - s_depth, s_y - 4.5, pe_z - 6.95))
tabs = [Part.makeBox(s_lug_l, 4.8, 0.5, V(oL - s_depth - s_lug_l, s_y - 2.4, pe_z + dz)) for dz in (-3.5, 3.0)]
switch = bezel.fuse([rocker, sbody] + tabs)

def mosfet(y0):
    pcb = Part.makeBox(mL, mW, mT, V(m_x0, y0, m_z))
    for (u, v) in m_holes:
        pcb = pcb.cut(Part.makeCylinder(1.5, mT + 1, V(m_x0 + u, y0 + v, m_z - 0.5)))
    t = m_z + mT
    term = Part.makeBox(7.6, 10.2, mH - mT, V(m_x0 + mL - 5.5 - 7.6, y0 + (mW - 10.2)/2, t))   # output terminal (+X end)
    term2 = Part.makeBox(7.6, 10.2, mH - mT, V(m_x0 + mL - 13.6 - 7.6, y0 + (mW - 10.2)/2, t)) # input terminal
    fet = Part.makeBox(6.6, 6.1, 2.3, V(m_x0 + mL - 22.0 - 6.6, y0 + (mW - 6.1)/2, t))          # IRFR120N DPAK
    hdr = Part.makeBox(2.54, 7.62, 8.5, V(m_x0 + 4.0, y0 + (mW - 7.62)/2, t))                   # SIG/VCC/GND header
    return pcb.fuse([term, term2, fet, hdr])
mos1, mos2 = mosfet(m_y[0]), mosfet(m_y[1])

def xt60(side):  # side -1: low-Y wall (faces -Y), +1: high-Y wall (faces +Y)
    wo = 0.0 if side < 0 else oW                      # outer wall face
    s = -side                                         # direction into the case
    def box(w, d, h, y_from, z0):                     # extends from y_from by d in direction s
        y0 = y_from if s > 0 else y_from - d
        return Part.makeBox(w, d, h, V(xt_cx - w/2, y0, z0))
    fl = box(xt_fl_w, xt_fl_t, xt_fl_h, wo - s*xt_fl_t, xt_z0)
    for sx in (-1, 1):
        fl = fl.cut(Part.makeCylinder(xt_hole_d/2, xt_fl_t + 2, V(xt_cx + sx*xt_hole_dx/2, wo - s*(xt_fl_t + 1), xt_zc), Y*s))
    f0 = wo - s*(xt_fl_t + xt_fr_d)
    front = box(xt_fr_w, xt_fr_d, xt_fr_h, f0, xt_zc - xt_fr_h/2)
    for dx in (-3.6, 3.6):                            # two socket bores
        front = front.cut(Part.makeCylinder(2.25, xt_fr_d + 0.2, V(xt_cx + dx, f0 - s*0.1, xt_zc), Y*s))
    body = box(xt_body_w, xt_body_d, xt_body_h, wo, xt_zc - xt_body_h/2)
    return fl.fuse([front, body])
xt1, xt2 = xt60(-1), xt60(+1)

# ================= DOCUMENT =================
doc = App.getDocument(DOC) if DOC in App.listDocuments() else App.newDocument(DOC)
for o in doc.Objects: doc.removeObject(o.Name)
lid_pl = App.Placement(V(0, 0, base_h + explode), App.Rotation())
def add(name, shp, col, tr=0, pl=None):
    f = doc.addObject("Part::Feature", name); f.Shape = shp
    if pl: f.Placement = pl
    if App.GuiUp:
        f.ViewObject.ShapeColor = col; f.ViewObject.Transparency = tr
    return f
fb = add("Case_Base", base, (0.15, 0.15, 0.18))
fl = add("Case_Lid", lid, (0.2, 0.45, 0.8), 20, lid_pl)
fk = add("Encoder_Knob", knob, (0.12, 0.12, 0.12), 0,
         App.Placement(V(e_cx, e_cy, base_h + explode + lid_t + k_gap), App.Rotation()))
add("ESP32S3_DevKitC1_Ref", esp, (0.1, 0.5, 0.2), 30)
add("OLED_1in54_128x64_Ref", oled, (0.05, 0.2, 0.55), 0, lid_pl)
add("Encoder_PEC11R_4115F_Ref", enc, (0.75, 0.75, 0.78), 0, lid_pl)
add("LM2596S_5V_Module_Ref", pmod, (0.1, 0.3, 0.75), 0)
add("DC_Jack_M8_5521_Ref", djack, (0.55, 0.55, 0.58), 0)
add("Switch_SMRS101_Ref", switch, (0.85, 0.2, 0.1), 0)
add("MOSFET_IRFR120N_1_Ref", mos1, (0.1, 0.45, 0.25), 0)
add("MOSFET_IRFR120N_2_Ref", mos2, (0.1, 0.45, 0.25), 0)
add("XT60E_F_1_Ref", xt1, (0.95, 0.8, 0.1), 0)
add("XT60E_F_2_Ref", xt2, (0.95, 0.8, 0.1), 0)
doc.recompute()

# ================= CHECKS & EXPORT =================
def at_lid(s, dz=0):
    c = s.copy(); c.translate(V(0, 0, base_h + dz)); return c
kn = knob.copy(); kn.translate(V(e_cx, e_cy, base_h + lid_t + k_gap))
parts = {"base": base, "lid": at_lid(lid), "knob": kn, "esp": esp, "oled": at_lid(oled), "enc": at_lid(enc),
         "pwr": pmod, "jack": djack, "switch": switch, "mos1": mos1, "mos2": mos2, "xt1": xt1, "xt2": xt2}
names, bad = list(parts), {}
for i in range(len(names)):
    for k in names[i+1:]:
        v = parts[names[i]].common(parts[k]).Volume
        if v > 0.01: bad[f"{names[i]}∩{k}"] = round(v, 2)
print("interferences:", bad or "none", "| valid:", base.isValid(), lid.isValid(), knob.isValid())
print("outer %.1f x %.1f x %.1f mm" % (oL, oW, base_h + lid_t))
if not App.GuiUp:
    print("WARNING: headless run – part colours are not saved; rebuild inside FreeCAD GUI to keep them")
doc.saveAs(OUT + ".FCStd")
# STLs in print orientation, sitting on z=0
base.exportStl(OUT + "_base.stl")
lp = lid.copy(); lp.rotate(V(0, 0, 0), X, 180); lp.translate(V(0, oW, lid_t)); lp.exportStl(OUT + "_lid.stl")   # outer face on bed
kp = knob.copy(); kp.rotate(V(0, 0, 0), X, 180); kp.translate(V(0, 0, k_h)); kp.exportStl(OUT + "_knob.stl")
