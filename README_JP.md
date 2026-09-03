# PyEarthCARE

PyEarthCAREは、JAXA版およびESA版の **EarthCARE Cloud Profiling Radar（CPR）** Level-2プロダクトから、レーダー反射強度およびDoppler velocityを含むvelocity関連物理量を読み込み、**緯度–高度断面図**として描画するためのPythonコード群です。

現在の構成は以下のとおりです。

```text
PyEarthCARE/
├── README.md
├── README_JP.md
├── lib/
│   └── PyEarthCARE.py
├── plot_jaxa_reflectivity.py
├── plot_jaxa_velocity.py
├── plot_esa_reflectivity.py
└── plot_esa_velocity.py
```

本リポジトリはEarthCARE CPRプロダクトの研究利用・可視化を目的としたものであり、**JAXAまたはESAの公式ソフトウェアではありません**。

[English README](README.md)

## 1. 機能

現在のコードでは、以下の処理に対応しています。

- EarthCARE HDF5ファイルを1ファイルずつ読み込む
- `--lat-min`および`--lat-max`で緯度範囲を指定する
- 1入力ファイルにつき1枚の緯度–高度断面図を作成する
- PNG形式でFigureを保存する
- JAXA版およびESA版の一部CPR Level-2プロダクトに対応する
- JAXA版では対応変数について1 km / 10 kmを切り替える
- velocity関連物理量は`--variable`で描画対象を選択する

横軸は**Latitude（緯度）**、縦軸は**Altitude（km）**です。

Figure上の緯度表示範囲は、指定したデータ抽出範囲より両側を0.03°広くしています。

```python
ax.set_xlim(lat_min - 0.03, lat_max + 0.03)
```

## 2. 対応プロダクトと変数

### 2.1 JAXA版 Reflectivity

使用コード：

```text
plot_jaxa_reflectivity.py
```

対象プロダクト：

```text
CPR_ECO
```

対応変数：

| オプション | HDF5変数名 |
|---|---|
| `--resolution 1km` | `integrated_radar_reflectivity_1km` |
| `--resolution 10km` | `integrated_radar_reflectivity_10km` |

デフォルトは`1km`です。

主に以下を読み込みます。

```text
/ScienceData/Geo/latitude
/ScienceData/Geo/bin_height
/ScienceData/Data/integrated_radar_reflectivity_1km
```

10 kmを指定した場合は、対応する`integrated_radar_reflectivity_10km`を使用します。

### 2.2 JAXA版 Velocity関連変数

使用コード：

```text
plot_jaxa_velocity.py
```

標準で使用する変数は、

```text
integrated_doppler_velocity
```

です。

実際のHDF5変数名に付く解像度のsuffixはコード側で自動的に追加します。例えば、

```bash
--variable integrated_doppler_velocity --resolution 1km
```

とした場合、

```text
integrated_doppler_velocity_1km
```

を読み込みます。

現在`--variable`で選択できる候補は以下です。

| `--variable` | 想定するJAXAプロダクト | 高度変数 |
|---|---|---|
| `integrated_doppler_velocity` | `CPR_ECO` | `bin_height` |
| `cloud_air_velocity` | `CPR_CLP` | `height` |
| `cloud_terminal_velocity1` | `CPR_CLP` | `height` |
| `cloud_terminal_velocity2` | `CPR_CLP` | `height` |
| `total_cloud_terminal_velocity` | `CPR_CLP` | `height` |

コマンドラインでは`1km`または`10km`を指定できます。ただし、指定した解像度の変数が実際に入力HDF5ファイル内に存在する必要があります。

`integrated_doppler_velocity`については、同じ`CPR_ECO`ファイル内に対応するintegrated radar reflectivityが存在する場合、それも読み込み、reflectivityが`-21 dBZ`未満の領域をvelocity描画から除外します。

JAXA版velocityについては、元となった解析Notebookの符号規約を維持し、描画時に以下の変換を行います。

```python
plot_velocity = -1.0 * velocity
```

### 2.3 ESA版 Reflectivity

使用コード：

```text
plot_esa_reflectivity.py
```

対象プロダクト：

```text
CPR_FMR
```

描画変数：

```text
reflectivity_corrected
```

`/ScienceData`以下の、

```text
latitude
height
reflectivity_corrected
```

を使用します。

### 2.4 ESA版 Velocity関連変数

使用コード：

```text
plot_esa_velocity.py
```

対象プロダクト：

```text
CPR_CD
```

標準変数：

```text
doppler_velocity_best_estimate
```

現在の選択候補は、

```text
doppler_velocity_best_estimate
sedimentation_velocity_best_estimate
doppler_velocity_integrated
```

です。

`--variable`を使って描画対象を変更できます。指定した変数が入力ファイルに存在しない場合はエラーになります。

ESA版velocityについては、JAXA版のような追加の符号反転を行わず、プロダクトに格納されている符号をそのまま描画します。

## 3. 必要環境

コードではPython 3.10以降を必要とする構文を使用しているため、**Python 3.10以上**を使用してください。

主なPythonライブラリは以下です。

```text
numpy
matplotlib
xarray
```

さらに、xarrayからEarthCARE HDF5ファイルを開くためのバックエンドが必要です。一般的な構成例は以下です。

```bash
python3 -m pip install numpy matplotlib xarray h5netcdf h5py
```

使用環境やHDF5ファイルの形式によっては、別のxarray対応HDF5/netCDFバックエンドを使用することもできます。

## 4. 導入

リポジトリをcloneまたはダウンロードし、リポジトリのディレクトリへ移動します。

```bash
git clone <repository-url>
cd PyEarthCARE
```

各描画コードは、

```text
lib/PyEarthCARE.py
```

から共通のデータ読み込み処理をimportします。

現段階ではPython packageとしてのインストール処理は不要です。

利用可能なオプションは以下で確認できます。

```bash
python3 plot_jaxa_reflectivity.py --help
python3 plot_jaxa_velocity.py --help
python3 plot_esa_reflectivity.py --help
python3 plot_esa_velocity.py --help
```

## 5. 使用方法

### 5.1 JAXA版 Reflectivity：1 km

```bash
python3 plot_jaxa_reflectivity.py \
    input_file.h5 \
    --output output_1km.png \
    --lat-min 36.0 \
    --lat-max 37.0 \
    --resolution 1km
```

### 5.2 JAXA版 Reflectivity：10 km

```bash
python3 plot_jaxa_reflectivity.py \
    input_file.h5 \
    --output output_10km.png \
    --lat-min 36.0 \
    --lat-max 37.0 \
    --resolution 10km
```

### 5.3 JAXA版 Integrated Doppler Velocity

```bash
python3 plot_jaxa_velocity.py \
    input_file.h5 \
    --output jaxa_velocity.png \
    --lat-min 36.0 \
    --lat-max 37.0 \
    --resolution 1km \
    --variable integrated_doppler_velocity
```

### 5.4 JAXA版 Cloud Air Velocity

`CPR_CLP`ファイルを入力します。

```bash
python3 plot_jaxa_velocity.py \
    input_file.h5 \
    --output jaxa_cloud_air_velocity.png \
    --lat-min 36.0 \
    --lat-max 37.0 \
    --resolution 1km \
    --variable cloud_air_velocity
```

### 5.5 ESA版 Corrected Reflectivity

```bash
python3 plot_esa_reflectivity.py \
    input_file.h5 \
    --output esa_reflectivity.png \
    --lat-min 36.0 \
    --lat-max 37.0
```

### 5.6 ESA版 Doppler Velocity

```bash
python3 plot_esa_velocity.py \
    input_file.h5 \
    --output esa_velocity.png \
    --lat-min 36.0 \
    --lat-max 37.0 \
    --variable doppler_velocity_best_estimate
```

## 7. 主なコマンドラインオプション

| オプション | 内容 |
|---|---|
| `input_file` | 入力するEarthCARE HDF5ファイル |
| `--output` | 出力PNGのファイル名またはパス |
| `--lat-min` | データ抽出に使用する最小緯度 |
| `--lat-max` | データ抽出に使用する最大緯度 |
| `--resolution` | JAXA版の解像度。`1km`または`10km` |
| `--variable` | 描画するvelocity関連変数 |
| `--dpi` | 出力Figureのdpi。デフォルトは600 |

`--resolution`はJAXA版コードで使用します。  
`--variable`はvelocity描画コードで使用します。

## 8. Figureの設定

現在の描画コードでは、以下を基本仕様としています。

- 1入力ファイルにつき1 Figure
- 1 Figureにつき1枚の緯度–高度断面図
- 横軸はLatitude
- 縦軸はAltitude (km)
- 高度表示範囲は概ね`-0.1–20.2 km`
- 出力形式はPNG
- デフォルトは600 dpi

Reflectivityについては、元コードと同様に`-21 dBZ`を基準とした低反射強度領域の処理を残しています。

標準的なvelocityの発散型カラースケールは概ね`-3.6–3.6 m s-1`です。

カラーマップ、level、軸範囲、ラベルなどのFigure固有設定は、利用者が容易に変更できるように`lib/PyEarthCARE.py`ではなく各`plot_*.py`内に残しています。

## 9. `lib/PyEarthCARE.py`

`lib/PyEarthCARE.py`には、JAXA版・ESA版に共通する読み込みおよび前処理をまとめています。

主な関数は以下です。

```python
read_jaxa_reflectivity()
read_jaxa_velocity()
read_esa_reflectivity()
read_esa_velocity()
select_latitude_range()
```

このライブラリでは主に、

- 入力ファイルの存在確認
- 必要なHDF5変数の存在確認
- 配列を`(profile, vertical_bin)`へそろえる処理
- 1次元または2次元の高度配列の調整
- 指定緯度範囲の抽出
- 必要変数が存在しない場合の利用可能変数一覧の表示

を行います。

Figureの描画条件やカラーマップなどは各`plot_*.py`側で管理します。

## 10. 注意事項

- JAXA版`integrated_doppler_velocity`は`CPR_ECO`を想定しています。
- JAXA版のcloud velocity関連変数は`CPR_CLP`を想定しています。
- ESA版corrected reflectivityは`CPR_FMR`を想定しています。
- ESA版velocity関連変数は`CPR_CD`を想定しています。
- 現在は横軸としてLatitudeを使用しており、沿軌道距離や時刻には対応していません。

## 11. 追加を推奨する公式資料・データ入手先

以下は、プロダクト定義、version、release note、データ入手方法を確認するためにREADMEへ追加することを推奨する公式ページです。

- JAXA EarthCAREプロダクト一覧：  
  https://www.eorc.jaxa.jp/EARTHCARE/data/prd_list_j.html
- JAXA EarthCARE資料室（ATBD、PDD、release note等）：  
  https://www.eorc.jaxa.jp/EARTHCARE/document/doc_index_j.html
- JAXA G-Portal（地球観測データ検索・ダウンロード）：  
  https://gportal.jaxa.jp/gpr/
- ESA Earth Online EarthCARE mission/data gateway：  
  https://earth.esa.int/eogateway/missions/earthcare

本リポジトリの基本参照先として、以下のページも併せて参照してください。

- JAXA EarthCAREページ：  
  https://www.eorc.jaxa.jp/EARTHCARE/index_j.html
- ESA EarthCARE Product Handbook：  
  https://earthcarehandbook.earth.esa.int/
- A-Train紹介・モニタリング資料（JAXA）：  
  https://www.eorc.jaxa.jp/EARTHCARE/A-train/A-train_monitor_documents_j.html
