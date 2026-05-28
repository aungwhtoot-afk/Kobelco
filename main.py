import flet as ft
import math

def main(page: ft.Page):
    # App နာမည်ကို Kobelco လို့ ပြောင်းထားပါတယ်
    page.title = "Kobelco RK250 Lift Planner"
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # 📱 Mobile အတွက် အပေါ်ခေါင်းစဉ်ဘား (AppBar)
    page.appbar = ft.AppBar(
        title=ft.Text("Kobelco Smart Planner", weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
        bgcolor=ft.colors.BLUE_700,
        center_title=True,
    )
    
    # Kobelco RK250 Load Chart Data
    max_front_caps = {
        9.32:  {3.0: 25.0, 4.0: 23.0, 5.0: 19.4, 6.0: 16.3},
        16.42: {5.0: 16.7, 8.0: 10.9, 10.0: 7.4, 12.0: 5.45},
        23.52: {6.0: 11.2, 10.0: 7.05, 14.0: 4.15, 16.0: 3.45},
        30.62: {8.0: 7.0, 12.0: 4.95, 16.0: 3.15, 20.0: 1.9, 24.0: 1.15}
    }

    crane_database = {
        6.3: {
            "360": max_front_caps
        },
        5.9: {
            "front": max_front_caps,
            "side": {
                9.32:  {3.0: 25.0, 4.0: 23.0, 5.0: 19.4, 6.0: 15.1},
                16.42: {5.0: 16.7, 8.0: 10.95, 10.0: 6.9, 12.0: 4.9},
                23.52: {6.0: 11.2, 10.0: 6.9, 14.0: 4.0, 16.0: 3.0},
                30.62: {8.0: 7.0, 12.0: 4.9, 16.0: 3.0, 20.0: 1.65}
            }
        },
        5.1: {
            "front": max_front_caps,
            "side": {
                9.32:  {3.0: 25.0, 4.0: 23.0, 5.0: 18.1, 6.0: 12.9},
                16.42: {5.0: 15.6, 8.0: 9.65, 10.0: 6.20, 12.0: 4.30},
                23.52: {6.0: 11.2, 10.0: 6.90, 14.0: 3.75, 16.0: 2.80},
                30.62: {8.0: 7.0, 12.0: 4.90, 16.0: 3.00, 20.0: 1.65, 24.0: 0.90}
            }
        },
        3.8: {
            "front": max_front_caps,
            "side": {
                9.32:  {3.0: 25.0, 4.0: 15.7, 5.0: 10.6, 6.0: 7.7, 7.0: 5.5},
                16.42: {5.0: 10.5, 8.0: 5.15, 10.0: 3.25, 12.0: 2.25},
                23.52: {6.0: 7.5, 10.0: 3.5, 14.0: 1.85, 16.0: 1.1},
                30.62: {8.0: 4.4, 12.0: 2.5, 16.0: 1.35, 20.0: 0.7}
            }
        },
        2.105: {
            "front": max_front_caps,
            "side": {
                9.32:  {3.0: 11.1, 4.0: 6.7, 5.0: 4.55, 6.0: 3.3},
                16.42: {5.0: 4.2, 8.0: 1.9, 10.0: 1.05},
                23.52: {6.0: 2.95, 10.0: 1.25, 12.0: 0.95},
                30.62: {8.0: 1.4, 12.0: 0.9}
            }
        }
    }
    single_line_pull = 3.5
    
    # အခြေခံ သတ်မှတ်ချက် အကွက်များ
    outrigger_dd = ft.Dropdown(
        label="Outrigger အကျယ် (m)", 
        options=[
            ft.dropdown.Option("6.3"), 
            ft.dropdown.Option("5.9"), 
            ft.dropdown.Option("5.1"),
            ft.dropdown.Option("3.8"),
            ft.dropdown.Option("2.105")
        ], 
        value="6.3"
    )
    
    area_dd = ft.Dropdown(label="မချီမည့် ဧရိယာ", options=[ft.dropdown.Option("360"), ft.dropdown.Option("front"), ft.dropdown.Option("side")], value="360")
    parts_in = ft.TextField(label="ကြိုးအရေအတွက် (Parts of line)", value="4", keyboard_type=ft.KeyboardType.NUMBER)
    
    # Tab 1 (Auto) အတွက် အကွက်များ
    t1_rad = ft.TextField(label="လိုအပ်သော Radius (m)", keyboard_type=ft.KeyboardType.NUMBER)
    t1_load = ft.TextField(label="မချီမည့် ဝန် (တန်)", keyboard_type=ft.KeyboardType.NUMBER)
    t1_res = ft.Text("", size=15, weight=ft.FontWeight.BOLD)
    
    # Tab 2 (Manual) အတွက် အကွက်များ
    t2_boom = ft.Dropdown(label="ထုတ်မည့် Boom အရှည် (m)", options=[ft.dropdown.Option("9.32"), ft.dropdown.Option("16.42"), ft.dropdown.Option("23.52"), ft.dropdown.Option("30.62")], value="16.42")
    t2_rad = ft.TextField(label="အကွာအဝေး Radius (m)", keyboard_type=ft.KeyboardType.NUMBER)
    t2_res = ft.Text("", size=15, weight=ft.FontWeight.BOLD)

    def get_safe_rad_and_cap(capacities, rad):
        keys = sorted(capacities.keys())
        if rad in keys:
            return rad, capacities[rad]
        if rad < keys[0]:
            return keys[0], capacities[keys[0]]
        if rad > keys[-1]:
            return None, None
            
        for i in range(len(keys) - 1):
            r1, r2 = keys[i], keys[i+1]
            if r1 < rad < r2:
                c1, c2 = capacities[r1], capacities[r2]
                interpolated_cap = c1 + (rad - r1) * (c2 - c1) / (r2 - r1)
                return rad, round(interpolated_cap, 2)
        return None, None

    def check_errors():
        area_val = area_dd.value.lower()
        o_val = outrigger_dd.value
        if o_val == "6.3" and area_val != "360":
            return "⚠️ Outrigger 6.3m တွင် '360' သာ ရွေးပါ။"
        if o_val != "6.3" and area_val == "360":
            return f"⚠️ Outrigger {o_val}m တွင် 'front' သို့မဟုတ် 'side' သာ ရွေးပါ။"
        return None

    def run_tab1(e):
        err = check_errors()
        if err:
            t1_res.value, t1_res.color = err, "orange"
            page.update()
            return
        try:
            rad_val = float(t1_rad.value)
            load_val = float(t1_load.value)
            rope_cap = int(parts_in.value) * single_line_pull
            booms = crane_database[float(outrigger_dd.value)][area_dd.value.lower()]
            found = False
            res_str = "📊 အလိုအလျောက် တွက်ချက်မှု:\n" + "-"*30 + "\n"
            for b_len, caps in booms.items():
                if rad_val < b_len:
                    calc_r, chart_c = get_safe_rad_and_cap(caps, rad_val)
                    if calc_r is not None:
                        max_load = min(chart_c, rope_cap)
                        if max_load >= load_val:
                            found = True
                            ang = math.degrees(math.acos(rad_val / b_len))
                            res_str += f"✅ Boom {b_len}m | {ang:.1f}°\n   မနိုင်ဝန်: {max_load} တန်\n\n"
            if not found:
                t1_res.value, t1_res.color = "❌ ဤဝန်အတွက် ချီနိုင်သော Boom မရှိပါ။", "red"
            else:
                t1_res.value, t1_res.color = res_str, "green"
        except:
            t1_res.value, t1_res.color = "ဂဏန်းများကို မှန်ကန်စွာ ထည့်ပါ။", "red"
        page.update()

    def run_tab2(e):
        err = check_errors()
        if err:
            t2_res.value, t2_res.color = err, "orange"
            page.update()
            return
        try:
            b_val = float(t2_boom.value)
            r_val = float(t2_rad.value)
            rope_cap = int(parts_in.value) * single_line_pull
            caps = crane_database[float(outrigger_dd.value)][area_dd.value.lower()][b_val]
            if r_val >= b_val:
                t2_res.value, t2_res.color = "❌ Radius သည် Boom ထက် မကြီးရပါ။", "red"
                page.update()
                return
            calc_r, chart_c = get_safe_rad_and_cap(caps, r_val)
            if calc_r is None:
                t2_res.value, t2_res.color = "❌ Radius လွန်နေပါသည်။", "red"
            else:
                max_load = min(chart_c, rope_cap)
                ang = math.degrees(math.acos(r_val / b_val))
                t2_res.value = f"📊 Boom {b_val}m တွက်ချက်မှု:\n" + "-"*30 + f"\n   ထောင့်: {ang:.1f}°\n   မနိုင်ဝန်: {max_load} တန်"
                t2_res.color = "green"
        except:
            t2_res.value, t2_res.color = "ဂဏန်းများကို မှန်ကန်စွာ ထည့်ပါ။", "red"
        page.update()

    auto_col = ft.Column([
        ft.Text("လိုချင်သော Radius နှင့် ဝန်ကို ထည့်ပါ-", italic=True),
        t1_rad, t1_load, ft.ElevatedButton("Boom ရှာမည်", on_click=run_tab1, bgcolor="blue", color="white"), t1_res
    ], visible=True, spacing=15)

    manual_col = ft.Column([
        ft.Text("ကိုယ်တိုင် Boom ရွေးပြီး တွက်ချက်ပါ-", italic=True),
        t2_boom, t2_rad, ft.ElevatedButton("တန်ချိန်တွက်မည်", on_click=run_tab2, bgcolor="green", color="white"), t2_res
    ], visible=False, spacing=15)

    def show_auto(e):
        auto_btn.bgcolor = "blue"
        manual_btn.bgcolor = "grey"
        auto_col.visible = True
        manual_col.visible = False
        page.update()

    def show_manual(e):
        auto_btn.bgcolor = "grey"
        manual_btn.bgcolor = "green"
        auto_col.visible = False
        manual_col.visible = True
        page.update()

    auto_btn = ft.ElevatedButton("Auto Planner", on_click=show_auto, bgcolor="blue", color="white")
    manual_btn = ft.ElevatedButton("Manual Check", on_click=show_manual, bgcolor="grey", color="white")
    tab_row = ft.Row([auto_btn, manual_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

    page.add(
        outrigger_dd, area_dd, parts_in, ft.Divider(),
        tab_row, ft.Divider(),
        auto_col, manual_col
    )

ft.app(target=main)

