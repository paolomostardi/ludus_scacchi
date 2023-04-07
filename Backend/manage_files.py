import requests


# Function to get user data from Lichess API
def get_user_data(username):
    url = f"https://lichess.org/api/user/{username}"
    response = requests.get(url)
    if response.ok:
        return response.json()
    else:
        return None


# Function to read usernames from file, get user data from API,
# and write usernames and ratings to another file
def write_user_ratings(input_file, output_file):
    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            # Read username from file
            username = line.strip().split()[1]
            # Get user data from API
            user_data = get_user_data(username)
            try:
                if user_data['perfs']['rapid']['rating']:
                    # Write user data to output file
                    rapid_rating = user_data['perfs']['rapid']['rating']
                    num_games = line.strip().split()[0]
                    f_out.write(f"{num_games} {username} {rapid_rating}\n")
                else:
                    print(f"Error retrieving data for {username}")
            except KeyError:
                print(username + 'is giving problems')

def sort_file(reading_file,writing_file):

    with open(reading_file, 'r') as f:
        lines = f.readlines()

    lines = [line.strip().split() for line in lines]
    lines = sorted(lines, key=lambda x: int(x[2]))

    with open(writing_file, 'w') as f:
        for line in lines:
            f.write(' '.join(line) + '\n')



input = r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\Backend\data\top_players_by_rating.txt'
output = r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\Backend\data\top_players_by_rating.txt'
sort_file(input,output)
