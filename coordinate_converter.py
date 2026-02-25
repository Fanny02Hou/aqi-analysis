#!/usr/bin/env python3
"""
座標系統轉換工具
WGS84 <-> TWD97 轉換
"""

import math

class CoordinateConverter:
    def __init__(self):
        # TWD97 參數 (TM2)
        self.a = 6378137.0  # WGS84 半長軸
        self.e2 = 0.0066943799901413165  # WGS84 離心率平方
        self.k0 = 0.9999  # 中央經線比例因子
        self.lon0 = math.radians(121)  # 中央經線
        self.lat0 = 0  # 原點緯度
        self.x0 = 250000  # 東偏
        self.y0 = 0  # 北偏
        
        # TWD97 投影參數
        self.E = 0.00669437999014133
        self.N0 = 0
        
    def wgs84_to_twd97(self, lat, lon):
        """WGS84 經緯度轉 TWD97 二度分帶座標"""
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        
        # 計算子午線弧長
        M = self._calculate_meridional_arc(lat_rad)
        
        # 計算中央經線差
        m = (lon_rad - self.lon0) * math.cos(lat_rad)
        
        # 計算曲率半徑
        N = self.a / math.sqrt(1 - self.e2 * math.sin(lat_rad)**2)
        
        # TWD97 座標
        x = self.x0 + self.k0 * N * m
        y = self.y0 + self.k0 * (M + N * math.tan(lat_rad) * m**2 / 2)
        
        return x, y
    
    def twd97_to_wgs84(self, x, y):
        """TWD97 二度分帶座標轉 WGS84 經緯度"""
        # 計算中央經線差
        m = (x - self.x0) / (self.k0 * self.a)
        
        # 初始緯度估計
        lat = self._estimate_latitude(y)
        
        # 迭代計算精確緯度
        for _ in range(5):
            N = self.a / math.sqrt(1 - self.e2 * math.sin(lat)**2)
            M = self._calculate_meridional_arc(lat)
            lat = lat + (y - self.y0 - self.k0 * M) / (self.k0 * N)
        
        # 計算經度
        lon = self.lon0 + m / math.cos(lat)
        
        return math.degrees(lat), math.degrees(lon)
    
    def _calculate_meridional_arc(self, lat_rad):
        """計算子午線弧長"""
        A = self.a * (1 - self.e2)
        B = self.a * (1 - self.e2) * (1 + self.e2/4 + 3*self.e2**2/64 + 5*self.e2**3/256)
        C = self.a * (1 - self.e2) * (3*self.e2/8 + 3*self.e2**2/32 + 45*self.e2**3/1024)
        D = self.a * (1 - self.e2) * (15*self.e2**2/256 + 45*self.e2**3/1024)
        E = self.a * (1 - self.e2) * (35*self.e2**3/3072)
        
        return A*lat_rad - B*math.sin(2*lat_rad) + C*math.sin(4*lat_rad) - D*math.sin(6*lat_rad) + E*math.sin(8*lat_rad)
    
    def _estimate_latitude(self, y):
        """估計緯度"""
        # 簡化的緯度估計
        lat = y / self.a
        return lat

# 使用範例
if __name__ == "__main__":
    converter = CoordinateConverter()
    
    # 台北車站 WGS84 座標
    lat_wgs, lon_wgs = 25.0478, 121.5170
    
    # 轉換為 TWD97
    x_twd, y_twd = converter.wgs84_to_twd97(lat_wgs, lon_wgs)
    print(f"WGS84 ({lat_wgs}, {lon_wgs}) -> TWD97 ({x_twd:.2f}, {y_twd:.2f})")
    
    # 轉回 WGS84
    lat_back, lon_back = converter.twd97_to_wgs84(x_twd, y_twd)
    print(f"TWD97 ({x_twd:.2f}, {y_twd:.2f}) -> WGS84 ({lat_back:.6f}, {lon_back:.6f})")
