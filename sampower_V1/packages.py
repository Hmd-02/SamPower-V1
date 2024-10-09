import pkg_resources

# Lister toutes les bibliothèques et leurs versions
installed_packages = pkg_resources.working_set

# Afficher chaque bibliothèque et sa version
for package in installed_packages:
    print(f"{package.key}=={package.version}")