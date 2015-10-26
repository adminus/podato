'use strict';

var browserify = require('browserify');
var gulp = require('gulp');
var source = require('vinyl-source-stream');
var buffer = require('vinyl-buffer');
var uglify = require('gulp-uglify');
var sourcemaps = require('gulp-sourcemaps');

var getBundleName = function () {
  var version = require('./package.json').version;
  var name = require('./package.json').name;
  return version + '.' + name + '.' + 'min';
};

gulp.task("javascript", function(){
    var bundler = browserify({
        entries: ['./webapp/static/jssrc/main.js'],
        debug: true
    });
    bundler.transform("babelify");
    bundler.transform("./configloader.js");

    var bundle = function() {
        return bundler
          .bundle()
          .pipe(source(getBundleName() + '.js'))
          .pipe(buffer())
          .pipe(sourcemaps.init({loadMaps: true}))
          //.pipe(uglify())
          .pipe(sourcemaps.write('../js'))
          .pipe(gulp.dest('./webapp/static/js/'));
    };

    return bundle();
});

gulp.task('watch', function() {
    gulp.watch("webapp/static/jssrc/**/*", ['javascript']);
})
