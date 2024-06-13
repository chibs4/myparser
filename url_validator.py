# pip install -U validators tldextract idna
# import idna  # Косячит если есть порт
import validators
from tldextract import TLDExtract

tld_extractor = (
    TLDExtract()
)  # Move it out of the function so as not to create a new instance with each call TLDExtract


def validate_domain_or_ip(input_str: str) -> bool:
    return validators.domain(input_str) or validators.ipv4(input_str)


def check_domain(input_str: str) -> tuple[str | None, str | None]:
    domain, port = input_str.split(":", 1) if ":" in input_str else (input_str, None)

    if (
        port
        and port.isdigit()
        and 0 < int(port) < 65536
        and validate_domain_or_ip(domain)
    ):
        return domain, port

    if validate_domain_or_ip(domain):
        return domain, None

    return None, None


def get_domain(url: str) -> str | None:
    if not url.strip():
        return None
    url = (
        url.lower()
        .strip("/")
        .split("//", 1)[-1]
        .split("/", 1)[0]
        .lstrip("www.")
        .strip()
    )
    return url.encode("idna").decode("utf-8")


def get_all_possible_subdomains(
    subdomain: str,
) -> tuple[str, ...]:  # TODO: uncomment for subdomains
    subdomains = subdomain.split(".")
    return tuple([".".join(subdomains[i:]) for i in range(len(subdomains))])


# TODO: uncomment for subdomains
# def validate_urls(urls: set[str]) -> tuple[set[str], set[tuple[str, tuple[str, ...]]]]:
#     subdomains = set()  # TODO: uncomment for subdomains
def validate_urls(urls: set[str]) -> set[str]:
    domains = set()

    for url in urls:
        if not (domain := get_domain(url)):
            continue

        domain, port = check_domain(domain)
        if not domain:
            continue

        extracted_tld = tld_extractor(domain)
        if result := extracted_tld.registered_domain:
            if port:
                result = f"{result}:{port}"

        elif result := extracted_tld.ipv4:
            if port:
                result = f"{result}:{port}"
        else:
            continue

        domains.add(result)

        # TODO: uncomment for subdomains
        # if subdomain := extracted_tld.subdomain:
        #     subdomains.add((result, get_all_possible_subdomains(subdomain)))

    return domains  # , subdomains  # TODO: uncomment for subdomains


def validate_url(url: str) -> str:
    if not (domain := get_domain(url)):
        return
    domain, port = check_domain(domain)
    if not domain:
        return
    extracted_tld = tld_extractor(domain)
    if result := extracted_tld.registered_domain:
        if port:
            result = f"{result}:{port}"
    elif result := extracted_tld.ipv4:
        if port:
            result = f"{result}:{port}"
    return domain


if __name__ == "__main__":

    # results, subs = validate_urls(  # TODO: uncomment for subdomains
    results = validate_urls(
        {
            "https://o.oo.ooo.oooo.foO.bar.com:8080",
            "o.oo.ooo.oooo.foO.bar.com:8080/",
            "/o.oo.ooo.oooo.foO.bar.com:8080",
            "//o.oo.ooo.oooo.foO.bar.com:8080",
            "o.oo.ooo.oooo.foO.bar.com:8080/r/redis/redis-stack/tags",
            "ftp://o.oo.ooo.oooo.foO.bar.com:8080/r/redis/redis-stack/tags",
            "www.o.oo.ooo.oooo.foO.bar.com",
            "https://hub.dOcker.com/r/redis/redis-stack/tags",
            "actually.not a url",
            "127.0.0.1:8000",
            "https://127.0.0.1:8000",
            "https://localhost:8000/docs",
            "http://forums.bbc.co.uk",
            "http://www.google.com",
            "//www.google1.com",
            "www.google2.com/",
            "лол.ололо.гоголе.рф",
        }
    )

    for res in results:
        print(res)

    # for sub in subs:  # TODO: uncomment for subdomains
    #     print(sub)
