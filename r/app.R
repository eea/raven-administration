library(plumber)

# --- Workspace directory (where CSVs etc. will be read/written) ---
WORKDIR <- Sys.getenv("R_WORKDIR", unset = "workspace")
if (!dir.exists(WORKDIR)) dir.create(WORKDIR, recursive = TRUE, showWarnings = FALSE)
setwd(WORKDIR)

# --- Persistent environment for this R session ---
.PERSIST_ENV <- new.env(parent = globalenv())

.capture_eval <- function(code_text) {
  env <- .PERSIST_ENV
  error_msg <- NULL
  result <- character()
  plot_b64 <- NULL
  plot_file <- tempfile(fileext = ".png")

  # Open a device for potential plotting
  grDevices::png(plot_file, width = 800, height = 600, res = 100)
  plot_empty <- TRUE   # assume nothing drawn

  tryCatch({
    result <- capture.output({
      # trace graphics::plot.new to detect base plotting activity
      trace(graphics::plot.new, exit = function() plot_empty <<- FALSE, print = FALSE)
      # trace grid.newpage as grid/lattice/ggplot2 may use grid graphics
      try(trace(grid::grid.newpage, exit = function() plot_empty <<- FALSE, print = FALSE), silent = TRUE)
      eval(parse(text = code_text), envir = env)
      # remove traces
      try(untrace(graphics::plot.new), silent = TRUE)
      try(untrace(grid::grid.newpage), silent = TRUE)
    })
  }, error = function(e) {
    error_msg <<- e$message
    result <<- character()
    try(untrace(graphics::plot.new), silent = TRUE)
    try(untrace(grid::grid.newpage), silent = TRUE)
  })

  # Close the device
  try(grDevices::dev.off(), silent = TRUE)

  # Only return image if something was drawn.
  # Some plotting systems (grid/lattice/ggplot2) don't call graphics::plot.new,
  # so accept the image if the output file indicates content was written.
  if (file.exists(plot_file)) {
    img_size <- file.info(plot_file)$size
    if (!plot_empty || img_size > 1000) {
      if (img_size > 0) {
        raw <- readBin(plot_file, what = "raw", n = img_size)
        plot_b64 <- jsonlite::base64_enc(raw)
      }
    }
  }

  list(
    output = paste(result, collapse = "\n"),
    plot = if (!is.null(plot_b64)) plot_b64 else "",
    error = error_msg,
    objects = ls(env)
  )
}

pr_obj <- pr() |>

  # List objects with tiny summary
  pr_get("/ls", function() {
    objs <- ls(.PERSIST_ENV)
    summary <- lapply(objs, function(nm) {
      obj <- get(nm, envir = .PERSIST_ENV)
      list(name = nm, class = class(obj)[1], length = tryCatch(length(obj), error = function(e) NA))
    })
    list(objects = summary, workdir = getwd())
  }) |>

# Reset workspace (clears variables; does NOT delete files)
  pr_post("/reset", function() {
    rm(list = ls(.PERSIST_ENV), envir = .PERSIST_ENV)
    list(ok = TRUE)
  }) |>

  # Execute arbitrary R code (persistent session)
  pr_post("/run", function(code = "") {
    .capture_eval(code)
  })


# --- Start server with logging ---
cat("🚀 Starting R API on http://0.0.0.0:8888\n")
flush.console()
pr_obj$run(host = "0.0.0.0", port = as.integer(Sys.getenv("R_PORT", unset = "8888")))