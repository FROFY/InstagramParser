from InstagramParser import InstagramParser


def main():
    parser = InstagramParser(
        "https://www.instagram.com/cristiano",
        "",
        ""
    )
    # parser.login_first_time()
    parser.login()
    parser.parse_posts_data(10)
    parser.write_to_csv()
    # parser.parse_short_data()
    # print(parser.get_short_data())


if __name__ == '__main__':
    main()
