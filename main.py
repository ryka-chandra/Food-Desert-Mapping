import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt


def load_in_data(census_file, food_access_file):
    """
    Takes two parameters, the filename for the census dataset and the
    filename for the food access dataset, merges the two datasets on
    CTIDFP00 / CensusTract and returns the result as a GeoDataFrame
    """
    census_data = gpd.read_file(census_file)
    food_access_data = pd.read_csv(food_access_file).iloc[:, 1:]
    merged_data = census_data.merge(food_access_data, left_on='CTIDFP00',
                                    right_on='CensusTract', how='left')
    return merged_data


def percentage_food_data(merged_data):
    """
    Takes the merged data and returns the percentage of census tracts
    in Washington for which we have food access data
    """
    wa_tracts = merged_data[merged_data['State'] == 'WA']
    wa_census_tracts_count = merged_data['CTIDFP00'].nunique()
    wa_food_tracts_count = wa_tracts['CTIDFP00'].nunique()
    percentage = wa_food_tracts_count / wa_census_tracts_count * 100
    return percentage


def plot_map(merged_data):
    """
    Takes the merged data and plots the shapes of all the census
    tracts in Washington in a file map.png
    """
    merged_data.plot()
    plt.title('Washington State')
    plt.savefig('map.png')


def plot_population_map(merged_data):
    """
    Takes the merged data and plots the shapes of all the census
    tracts in Washington in a file population_map.png where each
    census tract is colored according to population
    """
    wa_tracts = merged_data[merged_data['State'] == 'WA']
    ax = merged_data.plot(color='#EEEEEE')
    ax = wa_tracts.plot(ax=ax, column='POP2010', legend=True)
    ax.set_title('Washington Census Tract Populations')
    plt.savefig('population_map.png')


def plot_population_county_map(merged_data):
    """
    Takes the merged data and plots the shapes of all the census
    tracts in Washington in a file county_population_map.png where
    each county is colored according to population
    """
    wa_tracts = merged_data[merged_data['State'] == 'WA']
    county_pop = wa_tracts.groupby('County')['POP2010'].sum()
    wa_tracts = wa_tracts.merge(county_pop, left_on='County',
                                right_index=True, how='left',
                                suffixes=['_tracts', '_county'])
    ax = merged_data.plot(color='#EEEEEE')
    ax = wa_tracts.plot(column='POP2010_county', legend=True, ax=ax)
    ax.set_title('Washington County Populations')
    plt.savefig('county_population_map.png')


def plot_food_access_by_county(merged_data):
    """
    Takes the merged data and produces 4 plots on the same
    figure showing information about food access across income
    level in a file county_food_access.png
    """
    wa_tracts = merged_data[merged_data['State'] == 'WA']
    wa_tracts = wa_tracts[['County', 'geometry', 'POP2010', 'lapophalf',
                           'lapop10', 'lalowihalf', 'lalowi10']]
    c_data = wa_tracts.groupby('County').sum()
    c_data['lapophalf_ratio'] = c_data['lapophalf'] / c_data['POP2010']
    c_data['lapop10_ratio'] = c_data['lapop10'] / c_data['POP2010']
    c_data['lalowihalf_ratio'] = c_data['lalowihalf'] / c_data['POP2010']
    c_data['lalowi10_ratio'] = c_data['lalowi10'] / c_data['POP2010']

    wa_tracts = wa_tracts.merge(c_data, left_on='County', right_index=True,
                                how='left', suffixes=['_tracts', '_county'])
    fig, [[ax1, ax2], [ax3, ax4]] = plt.subplots(2, 2, figsize=(20, 10))
    merged_data.plot(color='#EEEEEE', ax=ax1)
    wa_tracts.plot(column='lapophalf_ratio', legend=True,
                   ax=ax1, vmin=0, vmax=1)
    ax1.set_title('Low Access: Half')

    merged_data.plot(color='#EEEEEE', ax=ax3)
    wa_tracts.plot(column='lapop10_ratio', legend=True,
                   ax=ax3, vmin=0, vmax=1)
    ax3.set_title('Low Access: 10')

    merged_data.plot(color='#EEEEEE', ax=ax2)
    wa_tracts.plot(column='lalowihalf_ratio', legend=True,
                   ax=ax2, vmin=0, vmax=1)
    ax2.set_title('Low Access + Low Income: Half')

    merged_data.plot(color='#EEEEEE', ax=ax4)
    wa_tracts.plot(column='lalowi10_ratio', legend=True,
                   ax=ax4, vmin=0, vmax=1)
    ax4.set_title('Low Access + Low Income: 10')
    plt.savefig('county_food_access.png')


def plot_low_access_tracts(merged_data):
    """
    Takes the merged data and plots all census tracts considered
    “low access” in a file low_access.png
    """
    merged_data['new_tracts_half'] = 0
    merged_data['new_tracts_10'] = 0

    urbanmask = (merged_data['Urban'] == 1) & (
        (merged_data['lapophalf'] >= 500) | ((merged_data['lapophalf'] /
                                              merged_data['POP2010']) >= 0.33))
    merged_data.loc[urbanmask, 'new_tracts_half'] = 1
    ruralmask = (merged_data['Rural'] == 1) & (
        (merged_data['lapop10'] >= 500) | ((merged_data['lapop10'] /
                                            merged_data['POP2010']) >= 0.33))
    merged_data.loc[ruralmask, 'new_tracts_10'] = 1
    merged_data['low_access'] = (merged_data['new_tracts_half'] +
                                 merged_data['new_tracts_10'])

    fig, ax = plt.subplots()
    merged_data.plot(color='#EEEEEE', ax=ax)
    wa_tracts = merged_data[merged_data['State'] == 'WA']
    wa_tracts.plot(ax=ax, color='#AAAAAA')
    low_access = merged_data[merged_data['low_access'] == 1]
    low_access.plot(ax=ax)
    plt.title('Low Access Census Tracts')
    plt.savefig('low_access.png')


def main():
    """
    Calls the main method, loads in the dataset provided,
    and calls all of the functions
    """
    state_data = load_in_data(
        'food_access/washington.json',
        'food_access/food_access.csv'
    )
    print(percentage_food_data(state_data))
    plot_map(state_data)
    plot_population_map(state_data)
    plot_population_county_map(state_data)
    plot_food_access_by_county(state_data)
    plot_low_access_tracts(state_data)


if __name__ == '__main__':
    main()
