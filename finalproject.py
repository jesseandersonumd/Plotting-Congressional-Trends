#!/usr/bin/env python3

"""
Name: Jesse Anderson
Directory ID: 115944473
Date: 2020-12-16
Assignment: Final Project

"""

import re
import requests
import sys
from matplotlib import pyplot as plt

valid_range = list(range(102,117))

with open("key.txt") as fh:
    api_key = fh.read().strip()

headers = {"X-API-KEY": f"{api_key}"}

sessions = {"102": 1991, "103": 1993, "104": 1995, "105": 1997, "106": 1999,             
            "107": 2001, "108": 2003, "109": 2005, "110": 2007, "111": 2009,             
            "112": 2011, "113": 2013, "114": 2015, "115": 2017, "116": 2019
           }

def obtainrange(period):

  '''
  Purpose: To identity the values passed in as sessions, irrespective of the separator. 

  Parameters: A string of two integer values separated by a symbol.

  Output: The two values passed in separated as elements in a tuple. 

  '''
  # I wanted to recognize that users might not always use '-' even if they're asked to in the initial print statement. 
  # This is why I handled the pattern itself with a regex expression. Ideally, the user should specify two three digit numbers that are separated by a symbol.
  # The below expression handles this. 

  regex_expression = "(\d+).(\d+)"

  retrieved = re.findall(regex_expression,period)
  
  # I'm returning a tuple here so that I can quickly perform tuple unpacking in the function that directly proceeds this. 

  return retrieved[0]

def checkrange(period):
  '''
  Purpose: To check whether the two values returned from the obtainrange() function are within the valid range. 

  Parameters: A string that specifies the two values, passed into obtainrange() at start of function. 

  Output: A list including values from start:end+1, which are both within the valid range. 

  '''
  # A call to the function obtainrange() is deliberate here. The first thing I need to do is return a tuple with two values that I can check to see if they're within a valid range. 
  # I perform tuple unpacking to obtain the first value in the range and the second value in the range. I need to make sure that both fall within the range of numbers within valid_range. 
  start, end = obtainrange(period)

  # If either start or end are not in the valid range, then I enter the while loop below. 
  while (int(start) not in valid_range) or (int(end) not in valid_range):

    # I print out a helpful range reminding them of the strict range 102-116 (end inclusive) and then repeat my initial input() statement.
    print("One of your numbers was not in range 102-116. Revise.")
    period = str(input("Please enter a range start-end, with two sessions separated by a symbol like -, *, or &."))
    
    # I now create two new variables based on the updated range specified in the new input() statement. 
    new_start, new_end = obtainrange(period)

    # If in the event that these two new values are both within the valid_range list, then we set our initial start variable equal to our new_start variable
      # and end=new_end so that we have two correct, valid range values. 
    
    if (int(new_start) in valid_range) and (int(new_end) in valid_range):
      start = new_start
      end = new_end
      break
    else:
      continue
  
  # I finally create a list with a range of values from start to end, inclusive. 
  start = int(start)
  end = int(end)
  return list(range(start,end+1))

# Define class Member()
class Member():
  
  # Constructor that requires several parameters: first_name, last_name, date_of_birth, gender, party
  def __init__(self, first_name, last_name, date_of_birth, gender, party):
    self.first_name = first_name
    self.last_name = last_name
    self.date_of_birth = date_of_birth
    self.gender = gender
    self.party = party

  # Creating calculate_age method to calculate the age of the representative during each session
  def calculate_age(self, year):
    return int(year) - self.date_of_birth

def get(session, chamber):
    '''
      Purpose: The purpose of this function is to get a list of all the members that we can work with later.

      Returns: List of all members.

    '''
    formatted = f"https://api.propublica.org/congress/v1/{str(session)}/{chamber}/members.json"
    data = requests.get(formatted, headers=headers).json()
    members_list = data["results"][0]["members"]
    return members_list

def calculate_members(session, chamber):
    '''
    Purpose: This function will create a list of new Member objects with the dictionary data returned from a call to the get() function. 

    Parameters: A session number and a chamber - "house" or "senate"

    Output: A tuple object with the year corresponding to the session passed in and a list of Member objects. 
    '''

    # Finds value associated with session key. 
    year = sessions[str(session)]

    # Calls the function get() to retrieve the dictionary data for each representative. 
    new_members = get(session,chamber)

    # Creates an empty list to store dynamically created Member objects. 
    member_obj_list = []

    # Iterates through all dictionaries returned from previous get() call. 
    for i in range(len(new_members)):

      # Recognizes pattern across values associated with "date_of_birth" keys - selects year from new list. 
      date_of_birth = new_members[i]["date_of_birth"].split("-")[0]

      # Performs type conversion so that calculate_age() can be performed with the year. 
      date_of_birth = int(date_of_birth)

      # Creating new Member object.
      new_member = Member(new_members[i]["first_name"], new_members[i]["last_name"], date_of_birth, new_members[i]["gender"], new_members[i]["party"])
      
      # Append Member object to member_obj_list created outside of for loop. 
      member_obj_list.append(new_member)
    
    # Return tuple of year and list of all Member objects associated with that year. 
    return (year, member_obj_list)

def metric_calculations(session, chamber=None, metric=None, metric_desired=None):
    '''
    Purpose: Generalizable function used to search through list of Member objects and check whether specific metrics match the metric value desired, if specified. 

    Parameters: One positional arguments: session (for congressional session passed in).
      Three keyword arguments set to default values of None.
      metric: used to select specific attributes from combined Members list, such as gender or party. 
      metric_desired: used to check matches with Member.metric attributes values. 
    
    Returns: Averages for Member list specified based on arguments passed in. 

    '''
    
    # Initializing specific_members list, which will be filled with Member.calculate_age(year) results based on conditions below. 
    specific_members = []

    # Creating lists of Member objects for senate and house by calling calculate_members(). 
    senators = calculate_members(session, "senate")
    house = calculate_members(session, "house")

    # This condition checks whether the user passed in a metric to check. 
    if metric!=None:

      # If a metric is specified, extend the house Member list to include the senate Member list so that the metric can be checked across all objects. 
      house[1].extend(senators[1])

      # With newly extended list, iterate through each member. 
      for member in house[1]:

        # Use the getattr() built-in function to check whether the value for member.metric matches the metric_desired:
          # E.g.: member.party == "D" if metric="party"
        if getattr(member,metric) == metric_desired:
          
          # If there's a match, only then do I append the member to the specific_members list. 
          specific_members.append(member.calculate_age(house[0]))
        else:

          # If there's no match, I simply continue and check the next Member object. 
          continue
    
    # If there are no metrics specified, then I just calculate the ages of all Member objects depending on whether "house" or "senate" is specified. 
    else:
      if chamber=="house":
        for member in house[1]:
          # house[0] = year
          specific_members.append(member.calculate_age(house[0]))
      else:
        for member in senators[1]:
          # senators[0] = year
          specific_members.append(member.calculate_age(senators[0]))
    
    # The specific_members list is now only updated with the Member objects that either correspond to matches if metric is specified
      # or the chamber specified. 
    return round(sum(specific_members)/len(specific_members),2)




if __name__ == "__main__":
  user_input = sys.argv[1]
  congressional_period = checkrange(user_input)

  # Create list comprehensions by calling the metric_calculations() function with the appropriate parameters. 
  women = [metric_calculations(elem, metric="gender", metric_desired="F") for elem in congressional_period] 
  men = [metric_calculations(elem, metric="gender", metric_desired="M") for elem in congressional_period] 
  reps = [metric_calculations(elem, metric="party", metric_desired="R") for elem in congressional_period] 
  dems = [metric_calculations(elem, metric="party", metric_desired="D") for elem in congressional_period] 
  house = [metric_calculations(elem, chamber="house") for elem in congressional_period]
  senate = [metric_calculations(elem, chamber="senate") for elem in congressional_period]
  
  # Create a list comprehension of all the years that are associated with the sessions. 
  years = [sessions[str(elem)] for elem in congressional_period]
  
  # Plot graphic with all lines. 
  plt.plot(years,women,label="Women")
  plt.plot(years,men,label="Men")
  plt.plot(years,reps,label="Republicans")
  plt.plot(years,dems,label="Democrats")
  plt.plot(years,house,label="House")
  plt.plot(years,senate,label="Senate")
  plt.title("Years versus average ages for congressional representatives")
  plt.xlabel("Years")
  plt.ylabel("Average ages")
  
  # Putting legend outside of plot because it covers lines. 
  plt.legend(bbox_to_anchor=(1, 1))
  plt.show()

  # Print out general statistics for each session. 
  print("---General statistics---")
  for i in range(len(years)):
    print(f"Year: {years[i]}")
    print(f"Republican average: {reps[i]}")
    print(f"Democrat average: {dems[i]}")
    print(f"House average: {house[i]}")
    print(f"Senate average: {senate[i]}")
    print(f"Women average: {women[i]}")
    print(f"Men average: {men[i]}")
    print("\n")
