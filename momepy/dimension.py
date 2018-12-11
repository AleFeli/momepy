#!/usr/bin/env python
# -*- coding: utf-8 -*-

# dimension.py
# definitons of dimension characters

import geopandas as gpd  # to remove in the end
from tqdm import tqdm  # progress bar
from shapely.geometry import Polygon
import shapely.ops
from .shape import make_circle


def area(objects, column_name):
    """
    Calculate area of each object in given shapefile. It can be used for any
    suitable element (building footprint, plot, tessellation, block).

    Parameters
    ----------
    objects : GeoDataFrame
        GeoDataFrame containing objects to analyse
    column_name : str
        name of the column to save the values

    Returns
    -------
    GeoDataFrame
        GeoDataFrame with new column [column_name] containing resulting values.
    """
    # define new column
    objects[column_name] = None
    objects[column_name] = objects[column_name].astype('float')
    print('Calculating areas...')

    # fill new column with the value of area, iterating over rows one by one
    for index, row in tqdm(objects.iterrows(), total=objects.shape[0]):
        objects.loc[index, column_name] = row['geometry'].area

    print('Areas calculated.')
    return objects


def perimeter(objects, column_name):
    """
    Calculate perimeter of each object in given shapefile. It can be used for any
    suitable element (building footprint, plot, tessellation, block).

    Parameters
    ----------
    objects : GeoDataFrame
        GeoDataFrame containing objects to analyse
    column_name : str
        name of the column to save the values

    Returns
    -------
    GeoDataFrame
        GeoDataFrame with new column [column_name] containing resulting values.
    """
    # define new column
    objects[column_name] = None
    objects[column_name] = objects[column_name].astype('float')
    print('Calculating perimeters...')

    # fill new column with the value of perimeter, iterating over rows one by one
    for index, row in tqdm(objects.iterrows(), total=objects.shape[0]):
        objects.loc[index, column_name] = row['geometry'].length

    print('Perimeters calculated.')
    return objects


def height_os(objects, column_name, original_column='relh2'):
    """
    Copy values from GB Ordance Survey data.

    Function tailored to GB Ordance Survey data of OS Building Heights (Alpha).
    It will copy RelH2 (relative height from ground level to base of the roof) values to new column.

    Parameters
    ----------
    objects : GeoDataFrame
        GeoDataFrame containing objects to analyse
    column_name : str
        name of the column to save the values
    original_column : str
        name of column where is stored original height value


    Returns
    -------
    GeoDataFrame
        GeoDataFrame with new column [column_name] containing resulting values.
    """
    # define new column
    objects[column_name] = None
    objects[column_name] = objects[column_name].astype('float')
    print('Calculating heights...')

    # fill new column with the value of perimeter, iterating over rows one by one
    for index, row in tqdm(objects.iterrows(), total=objects.shape[0]):
        objects.loc[index, column_name] = row[original_column]

    print('Heights defined.')
    return objects


def height_prg(objects, column_name, floors_column='od_POCET_P', floor_type='od_TYP'):
    """
    Define building heights based on Geoportal Prague Data.

    Function tailored to Geoportal Prague.
    It will calculate estimated building heights based on floor number and type.

    Parameters
    ----------
    objects : GeoDataFrame
        GeoDataFrame containing objects to analyse
    column_name : str
        name of the column to save the values
    floor_type : str
        name of the column defining buildings type (to differentiate height of the floor)

    Returns
    -------
    GeoDataFrame
        GeoDataFrame with new column [column_name] containing resulting values.
    """
    # define new column
    objects[column_name] = None
    objects[column_name] = objects[column_name].astype('float')
    print('Calculating heights...')

    # fill new column with the value of perimeter, iterating over rows one by one
    for index, row in tqdm(objects.iterrows(), total=objects.shape[0]):
        if row[floor_type] == 7:
            height = row[floors_column] * 3.5  # old buildings with high ceiling
        elif row[floor_type] == 3:
            height = row[floors_column] * 5  # warehouses
        else:
            height = row[floors_column] * 3  # standard buildings

        objects.loc[index, column_name] = height

    print('Heights defined.')
    return objects


def volume(objects, column_name, area_column, height_column, area_calculated):
    """
    Calculate volume of each object in given shapefile based on its height and area.

    Parameters
    ----------
    objects : GeoDataFrame
        GeoDataFrame containing objects to analyse
    column_name : str
        name of the column to save the values
    area_column : str
        name of column where is stored area value
    height_column : str
        name of column where is stored height value
    area_calculated : bool
        boolean value checking whether area has been previously calculated and
        stored in separate column. If set to False, function will calculate areas
        during the process without saving them separately.

    Returns
    -------
    GeoDataFrame
        GeoDataFrame with new column [column_name] containing resulting values.
    """
    # define new column
    objects[column_name] = None
    objects[column_name] = objects[column_name].astype('float')
    print('Calculating volumes...')

    if area_calculated:
        try:
            # fill new column with the value of perimeter, iterating over rows one by one
            for index, row in tqdm(objects.iterrows(), total=objects.shape[0]):
                objects.loc[index, column_name] = row[area_column] * row[height_column]
            print('Volumes calculated.')

        except KeyError:
            print('ERROR: Building area column named', area_column, 'not found. Define area_column or set area_calculated to False.')
    else:
        # fill new column with the value of perimeter, iterating over rows one by one
        for index, row in tqdm(objects.iterrows(), total=objects.shape[0]):
            objects.loc[index, column_name] = row['geometry'].area * row[height_column]

        print('Volumes calculated.')
        return objects


def floor_area(objects, column_name, area_column, height_column, area_calculated):
    """
    Calculate floor area of each object based on height and area.

    Number of floors is simplified into formula height / 3
    (it is assumed that on average one floor is approximately 3 metres)

    Parameters
    ----------
    objects : GeoDataFrame
        GeoDataFrame containing objects to analyse
    column_name : str
        name of the column to save the values
    area_column : str
        name of column where is stored area value
    height_column : str
        name of column where is stored height value
    area_calculated : bool
        boolean value checking whether area has been previously calculated and
        stored in separate column. If set to False, function will calculate areas
        during the process without saving them separately.

    Returns
    -------
    GeoDataFrame
        GeoDataFrame with new column [column_name] containing resulting values.
    """
    # define new column
    objects[column_name] = None
    objects[column_name] = objects[column_name].astype('float')
    print('Calculating floor areas...')

    if area_calculated:
        try:
            # fill new column with the value of perimeter, iterating over rows one by one
            for index, row in tqdm(objects.iterrows(), total=objects.shape[0]):
                objects.loc[index, column_name] = row[area_column] * (row[height_column] // 3)

            print('Floor areas calculated.')

        except KeyError:
            print('ERROR: Building area column named', area_column, 'not found. Define area_column or set area_calculated to False.')
    else:
        # fill new column with the value of perimeter, iterating over rows one by one
        for index, row in tqdm(objects.iterrows(), total=objects.shape[0]):
            objects.loc[index, column_name] = row['geometry'].area * (row[height_column] // 3)

        print('Floor areas calculated.')
    return objects


def courtyard_area(objects, column_name, area_column, area_calculated):
    """
    Calculate area of holes within geometry - area of courtyards.

    Parameters
    ----------
    objects : GeoDataFrame
        GeoDataFrame containing objects to analyse
    column_name : str
        name of the column to save the values
    area_column : str
        name of column where is stored area value
    area_calculated : bool
        boolean value checking whether area has been previously calculated and
        stored in separate column. If set to False, function will calculate areas
        during the process without saving them separately.

    Returns
    -------
    GeoDataFrame
        GeoDataFrame with new column [column_name] containing resulting values.
    """
    # define new column
    objects[column_name] = None
    objects[column_name] = objects[column_name].astype('float')
    print('Calculating courtyard areas...')

    if area_calculated:
        try:
            for index, row in tqdm(objects.iterrows(), total=objects.shape[0]):
                objects.loc[index, column_name] = Polygon(row['geometry'].exterior).area - row[area_column]

            print('Core area indices calculated.')
        except KeyError:
            print('ERROR: Building area column named', area_column, 'not found. Define area_column or set area_calculated to False.')
    else:
        for index, row in tqdm(objects.iterrows(), total=objects.shape[0]):
            objects.loc[index, column_name] = Polygon(row['geometry'].exterior).area - row['geometry'].area

        print('Core area indices calculated.')
    return objects


def longest_axis_length(objects, column_name):
    """
    Calculate the length of the longest axis of object.

    Axis is defined as a diameter of minimal circumscribed circle around the convex hull.
    It does not have to be fully inside an object.

    Parameters
    ----------
    objects : GeoDataFrame
        GeoDataFrame containing objects to analyse
    column_name : str
        name of the column to save the values

    Returns
    -------
    GeoDataFrame
        GeoDataFrame with new column [column_name] containing resulting values.
    """
    # define new column
    objects[column_name] = None
    objects[column_name] = objects[column_name].astype('float')
    print('Calculating the longest axis...')

    # calculate the area of circumcircle
    def longest_axis(points):
        circ = make_circle(points)
        return(circ[2] * 2)

    def sort_NoneType(geom):
        if geom is not None:
            if geom.type is not 'Polygon':
                return(0)
            else:
                return(longest_axis(list(geom.boundary.coords)))
        else:
            return(0)

    # fill new column with the value of area, iterating over rows one by one
    for index, row in tqdm(objects.iterrows(), total=objects.shape[0]):
        objects.loc[index, column_name] = longest_axis(row['geometry'].convex_hull.exterior.coords)

    print('The longest axis calculated.')
    return objects


def effective_mesh(objects, column_name, spatial_weights, area_column):
    """
    Calculate the effective mesh size

    Effective mesh size of the area within k topological steps defined in spatial_weights.

    .. math::
        \\

    Parameters
    ----------
    objects : GeoDataFrame
        GeoDataFrame containing objects to analyse
    column_name : str
        name of the column to save the values
    spatial_weights : libpysal.weights
        spatial weights matrix
    area_column : str
        name of the column of objects gdf where is stored area value

    Returns
    -------
    GeoDataFrame
        GeoDataFrame with new column [column_name] containing resulting values.

    References
    ----------
    Hausleitner B and Berghauser Pont M (2017) Development of a configurational
    typology for micro-businesses integrating geometric and configurational variables.

    Notes
    -----
    Resolve the issues if there is no spatial weights matrix. Corellation with block_density()

    """
    # define new column
    objects[column_name] = None
    objects[column_name] = objects[column_name].astype('float')

    print('Calculating effective mesh size...')

    for index, row in tqdm(objects.iterrows(), total=objects.shape[0]):
        neighbours = spatial_weights.neighbors[index]
        total_area = row[area_column]
        for n in neighbours:
            n_area = objects.iloc[n][area_column]
            total_area = total_area + n_area

        objects.loc[index, column_name] = total_area / (len(neighbours) + 1)
# to be deleted, keep at the end

# path = "/Users/martin/Dropbox/StrathUni/PhD/Papers/Voronoi tesselation/Data/Zurich/Final data/Voronoi/test/voronoi_10.shp"
# objects = gpd.read_file(path)

# longest_axis_length2(objects, column_name='longest_axis')

# objects.head
# objects.to_file(path)
