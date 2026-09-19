args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1L) stop("Usage: Rscript setup_packages.R <project-library>")
lib <- normalizePath(args[1], winslash = "/", mustWork = FALSE)
dir.create(lib, recursive = TRUE, showWarnings = FALSE)
.libPaths(c(lib, .libPaths()))

normalize_version <- function(x) gsub("-", ".", as.character(x), fixed = TRUE)
required <- c(metafor = "5.0-1", clubSandwich = "0.7.0")
needs_install <- vapply(names(required), function(pkg) {
  !requireNamespace(pkg, quietly = TRUE) ||
    normalize_version(utils::packageVersion(pkg)) != normalize_version(required[[pkg]])
}, logical(1))

if (any(needs_install)) {
  if (!requireNamespace("remotes", quietly = TRUE)) {
    install.packages("remotes", lib = lib, repos = "https://cloud.r-project.org")
  }
  for (pkg in names(required)[needs_install]) {
    message("Installing ", pkg, " ", required[[pkg]], " into ", lib)
    remotes::install_version(
      package = pkg,
      version = required[[pkg]],
      lib = lib,
      repos = "https://cloud.r-project.org",
      dependencies = c("Depends", "Imports", "LinkingTo")
    )
  }
}

for (pkg in names(required)) {
  stopifnot(requireNamespace(pkg, quietly = TRUE))
  observed <- normalize_version(utils::packageVersion(pkg))
  if (observed != normalize_version(required[[pkg]])) {
    stop(pkg, " version mismatch: expected ", required[[pkg]], ", observed ", observed)
  }
  message(pkg, " ", observed, " OK")
}
