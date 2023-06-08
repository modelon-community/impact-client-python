const Configuration = {

    extends: ['@commitlint/config-conventional'],
    rules: {
        'body-max-line-length': [2, 'always', 500],
        'footer-max-line-length': [2, 'always', 500],
        'header-max-length': [2, 'always', 500]
    },

    ignores: [(commit) => commit.includes('BREAKING CHANGE: the upload_fmu method has been removed'),
    (commit) => commit.includes('BREAKING CHANGE: the upload_model_library method has been removed')]
};

module.exports = Configuration;