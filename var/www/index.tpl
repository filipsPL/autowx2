cat <<EOF
<!DOCTYPE html>
<html lang="en">

  <head>

    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="autowx2 atomated satellite receiving station">
    <meta name="author" content="filipsPL@github">

    <title>autowx2 atomated satellite receiving station :: $htmlTitle</title>

    <!-- Bootstrap core CSS -->
    <link href="$wwwRootPath/css/bootstrap.min.css" rel="stylesheet">

    <!-- Custom styles for this template -->
    <link href="$wwwRootPath/css/logo-nav.css" rel="stylesheet">


    <link  href="$wwwRootPath/css/fancybox/jquery.fancybox.min.css" rel="stylesheet">

  </head>

  <body>

    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
      <div class="container">
        <a class="navbar-brand" href="$wwwRootPath">
          autowx2 | automatic receiving station
        </a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarResponsive" aria-controls="navbarResponsive" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarResponsive">
          <ul class="navbar-nav ml-auto">
            <li class="nav-item active">
              <a class="nav-link" href="$wwwRootPath/index.html">Home
                <span class="sr-only">(current)</span>
              </a>
            </li>
            <li class="nav-item"> 
            <a class="nav-link" href="$wwwRootPath/table.html">Pass table</a>
          </li>
            <li class="nav-item">
              <a class="nav-link" href="https://github.com/filipsPL/autowx2">Source code</a>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Page Content -->
    <div class="container">

<div class="row">
  <div class="col-md-12">
  <h1>$htmlTitle</h1>
  Generated: $currentDate | version: $autowx2version

  $htmlBody
  </div>
</div>

    </div>
    <!-- /.container -->



    <!-- Bootstrap core JavaScript -->
    <script src="$wwwRootPath/css/jquery.min.js"></script>
    <script src="$wwwRootPath/css/bootstrap.bundle.min.js"></script>
    <script src="$wwwRootPath/css/fancybox/jquery.fancybox.min.js"></script>

  </body>

</html>
EOF
