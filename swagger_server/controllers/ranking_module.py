from github import Github, GithubException
import numpy as np
import datetime
import os
import sys


def output_result(scores, git_repos, unavailable_urls):
    try:
        assert len(git_repos) == len(scores[0])
    except AssertionError:
        return

    net_scores = merge_test_scores(scores, 6)  # 6 is current total weight
    net_scores, git_repos = sort_items(net_scores, git_repos)

    for i in range(len(git_repos) - 1, -1, -1):
        if scores[4][i] == 0:  # Compatible licence is mandatory
            print(f"{git_repos[i]} 0 {scores[0][i]} "
                  f"{scores[1][i]} {scores[2][i]} {scores[3][i]} {scores[4][i]}")
        else:
            print(f"{git_repos[i]} {net_scores[i]} {scores[0][i]} "
                  f"{scores[1][i]} {scores[2][i]} {scores[3][i]} {scores[4][i]}")
    for i in range(len(unavailable_urls)):
        print(f"{unavailable_urls[i]} -1 -1 -1 -1 -1 -1")



def sort_items(scores, urls):
    scores, urls = zip(*sorted(zip(scores, urls)))
    return scores, urls


def normalize_data(data):
    if data is None:
        return

    data = np.array(data)
    return ((data - data.min()) / (data.max() - data.min())).tolist()


def weigh_list(data, amount):
    return [x * amount for x in data]


def check_for_documentation(repos):
    readme_size = []
    for repo in repos:
        readme = repo.get_readme().decoded_content.decode().lower()
        if "documentation](https://" in readme or "doc](https://" in readme or "docs](https://" in readme:
            readme_size.append(len(readme) * 50)
        else:
            readme_size.append(len(readme))
    return readme_size


def merge_test_scores(all_lists, weight):  # If we'd like to weigh a list more, we'd need to change total weight
    print (all_lists)
    final_scores = [0] * len(all_lists[0])
    for lst in all_lists:
        final_scores = [a + b for a, b in zip(lst, final_scores)]
    return [round(x / weight, 1) for x in final_scores]


# Scoring functions
def get_license_scores(repos):
    licenses = []
    for repo in repos:
        try:
            info = repo.get_license().decoded_content.decode().lower()
        except GithubException:
            info = repo.get_readme().decoded_content.decode().lower()
        if "mit license" in info or 'general public license' in info:
            licenses.append(1)
        else:
            licenses.append(0)

    return licenses


def get_ramp_up_scores(repos):
    
    print (repos)
    project_size = normalize_data([-repo.size for repo in repos])

    stargazers = normalize_data([repo.stargazers_count for repo in repos])

    readme_value = normalize_data(check_for_documentation(repos))

    return merge_test_scores([project_size, stargazers, readme_value], 3)



def get_responsiveness_scores(repos):
    issues = normalize_data([repo.open_issues for repo in repos])

    days = [(repo.pushed_at - datetime.datetime.now()).days for repo in repos]

    days = weigh_list(normalize_data(days), 2)

    return weigh_list(merge_test_scores([issues, days], 3), 2)  # This is important, so double weight



def get_bus_factor_scores(repos):
    
    bus_factor_scores = [len(repo.get_contents("")) / repo.get_contributors().totalCount for repo in repos]

    return [round(x, 1) for x in normalize_data(bus_factor_scores)]


def get_correctness_scores(repos):

    forks = normalize_data([repo.forks_count for repo in repos])
    subscribers = normalize_data([repo.subscribers_count for repo in repos])
    stars = normalize_data([repo.stargazers_count for repo in repos])

    return merge_test_scores([forks, subscribers, stars], 3)


def run(desired_repo):
    
    try:
        TOKEN = os.getenv('TOKEN')
    except KeyError:
        print ("Nope, no token\n")
        sys.exit()
    
    # Initialize
    try:
        g = Github(login_or_token=TOKEN)
    except GithubException:
        return

    repo = g.get_repo(desired_repo)
    flat_repo = g.get_repo("strapi/strapi")
    random_repo = g.get_repo("jackfrued/Python-100-Days")
    repos = [repo, flat_repo, random_repo]


    scores = [get_ramp_up_scores(repos), 
              get_correctness_scores(repos),
              get_bus_factor_scores(repos), 
              get_responsiveness_scores(repos), 
              get_license_scores(repos)]


    print (scores)
    print ("\n\n\n")
    # What the fuck?
        # I think this prints ramp up for each repo first
    output_result(scores, desired_repo, None)
    
run("gjairath/language-learner")