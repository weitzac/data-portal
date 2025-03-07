<template>
  <div class="dataset-details">
    <div class="header">
      <div class="gradient">
        <el-row type="flex" justify="center">
          <el-col :xs="22" :sm="22" :md="22" :lg="18" :xl="16">
            <div class="breadcrumb">
              <el-row>
                <el-col :span="24">
                  Browse Data / {{ datasetName }}
                </el-col>
              </el-row>
            </div>
          </el-col>
        </el-row>
      </div>
    </div>
    <div class="discover-content container-fluid">
      <dataset-header :dataset-details="datasetDetails" />
    </div>

    <el-row type="flex" justify="center">
      <el-col :xs="22" :sm="22" :md="22" :lg="18" :xl="16">
        <div
          v-loading="loadingMarkdown"
          class="col-xs-12 description-container"
          v-html="parsedMarkdown"
        />
      </el-col>
    </el-row>

    <el-row type="flex" justify="center">
      <el-col :xs="22" :sm="22" :md="22" :lg="18" :xl="16">
        <h2>Files</h2>
        <files-table :dataset-details="datasetDetails" />
      </el-col>
    </el-row>

    <div class="dataset-info">
      <div class="discover-content container-fluid dataset-info-container">
        <el-row type="flex" justify="center">
          <el-col :xs="22" :sm="22" :md="22" :lg="18" :xl="16">
            <el-row type="flex" justify="center">
              <el-col :span="24">
                <h2>
                  About this dataset
                </h2>
              </el-col>
            </el-row>
            <el-row class="mb-24">
              <el-col
                class="info-publishing-history"
                :span="24"
              >
                <div class="info-text">
                  {{ lastUpdatedDate }}
                  <div class="info-text-caps">
                    Last Updated
                  </div>
                </div>
              </el-col>
            </el-row>
            <el-row type="flex" justify="center">
              <el-col :span="24">
                <h3>
                  Cite this dataset
                </h3>
                <div
                  v-loading="citationLoading"
                  class="info-citation"
                  aria-live="polite"
                  v-html="$sanitize(citationText, ['i'])"
                />
                <div class="info-citation-links mb-24">
                  Formatted as:
                  <button
                    title="Format citation apa"
                    :class="{active: activeCitation === 'apa'}"
                    @click="handleCitationChanged('apa')"
                  >
                    APA
                  </button>
                  <button
                    title="Format citation chicago"
                    :class="{active: activeCitation === 'chicago-note-bibliography'}"
                    @click="handleCitationChanged('chicago-note-bibliography')"
                  >
                    Chicago
                  </button>
                  <button
                    title="Format citation ieee"
                    :class="{active: activeCitation === 'ieee'}"
                    @click="handleCitationChanged('ieee')"
                  >
                    IEEE
                  </button>
                  <a
                    :href="`https://crosscite.org/?doi=${datasetDetails.doi}`"
                    target="_blank"
                  >
                    More on Crosscite.org
                  </a>
                </div>
              </el-col>
            </el-row>
            <el-row type="flex" justify="center">
              <el-col :span="24">
                <h3>Tags</h3>
                <tag-list :tags="datasetTags" />
              </el-col>
            </el-row>
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>

<script>
import marked from 'marked'
import {
  compose,
  head,
  propOr
} from 'ramda'
// import { mapState } from 'vuex'

import DatasetHeader from '../DatasetHeader/DatasetHeader.vue'
import TagList from '../TagList/TagList.vue'
import FilesTable from '../FilesTable/FilesTable.vue'

import Request from '../../mixins/request'
import DateUtils from '../../mixins/format-date'

marked.setOptions({
  sanitize: true
})

export default {
  name: 'DatasetDetails',

  components: {
    DatasetHeader,
    FilesTable,
    TagList
  },

  mixins: [
    Request,
    DateUtils
  ],

  props: {
    showSignupFooter: {
      type: Boolean,
      default: false
    },
    datasetId: {
      type: Number,
      default: null
    }
  },

  data () {
    return {
      citationText: '',
      activeCitation: '',
      showCopySuccess: false,
      citationLoading: false,
      isTombStone: false,
      isLoadingDataset: false,
      datasetDetails: {},
      errorLoading: false,
      loadingMarkdown: false,
      markdown: ''
    }
  },

  computed: {
    /**
     * Parses the markdown text
     */
    parsedMarkdown: function () {
      return marked(this.markdown)
    },

    /**
     * Get formatted originally published date
     * @return {String}
     */
    originallyPublishedDate: function () {
      const date = propOr('', 'createdAt', this.datasetDetails)
      return this.formatDate(date)
    },
    /**
     * Get formatted last updated date
     * @return {String}
     */
    lastUpdatedDate: function () {
      const date = propOr('', 'updatedAt', this.datasetDetails)
      return this.formatDate(date)
    },
    /**
     * Returns list of tags for dataset
     * @returns {Array}
     */
    datasetTags: function () {
      return propOr([], 'tags', this.datasetDetails)
    },
    /**
     * Returns the current location href from the window object
     * @returns {String}
     */
    thisUrl: function () {
      return window.location.origin + this.$route.fullPath
    },
    /**
     * Return DOI link
     * @returns {String}
     */
    DOIlink: function () {
      const doi = propOr('', 'doi', this.datasetDetails)
      return doi
        ? `https://doi.org/${doi}`
        : ''
    },

    /**
     * Compute description
     * @returns {String}
     */
    datasetDescription: function () {
      return propOr('', 'description', this.datasetDetails)
    },

    /**
     * Compute name
     * @returns {String}
     */
    datasetName: function () {
      return propOr('', 'name', this.datasetDetails)
    },

    /**
     * Compute organization name
     * @returns {String}
     */
    organizationName: function () {
      return propOr('', 'organizationName', this.datasetDetails)
    },

    /**
     * Compute endpoint URL to get dataset
     * @returns {String}
     */
    getDatasetUrl: function () {
      return `https://api.blackfynn.io/discover/datasets/${this.datasetId}`
    }
  },

  watch: {
    DOIlink: {
      handler: function (val) {
        if (val) {
          this.handleCitationChanged('apa')
        }
      },
      immediate: true
    },
    getDatasetUrl: {
      handler: function (val) {
        if (val) {
          this.getDataset()
        }
      },
      immediate: true
    },

    datasetDetails: {
      handler: function () {
        this.getMarkdown()
      },
      immediate: true
    }
  },

  methods: {

    getDataset: function () {
      this.isLoadingDataset = true

      this.axios.get(this.getDatasetUrl)
        .then(response => {
          this.datasetDetails = response.data
        })
        .catch(error => {
          // handle error
          this.errorLoading = true
        })
        .finally(() => {
          this.isLoadingDataset = false
        });
    },

    /**
     * Confirms that url of dataset was copied successfully
     * and sets boolean to true
     */
    onCopySuccess: function () {
      this.showCopySuccess = true
    },
    /**
     * gets bibiolography based on citation type for current DOI
     * @param {String} citationType
     */
    handleCitationChanged: function (citationType) {
      if (citationType === this.activeCitation) {
        return
      }
      this.citationLoading = true
      this.activeCitation = citationType
      // find all citation types at https://github.com/citation-style-language/style
      const doi = propOr('', 'doi', this.datasetDetails)
      const url = `https://citation.crosscite.org/format?doi=${doi}&style=${citationType}&lang=en-US`
      return fetch(url)
        .then(response => {
          return response.text()
        })
        .then(text => {
          this.citationText = text
        })
        .finally(() => {
          this.citationLoading = false
        })
    },

    /**
     * Get markdown logic from details response
     */
    getMarkdown: function () {
      this.loadingMarkdown = true
      const readme = propOr('', 'readme', this.datasetDetails)
      if (readme !== '') {
        fetch(readme)
          .then(response => response.text())
          .then(response => {
            this.loadingMarkdown = false
            this.markdown = response
          })
          .catch(error => {
            throw (error)
          })
      }
    }
  },

  metaInfo () {
    return {
      meta: [
        {
          name: 'DC.identifier',
          content: this.DOIlink,
          scheme: 'DCTERMS.URI'
        },
        {
          name: 'DC.publisher',
          content: this.organizationName
        },
        {
          name: 'DC.date',
          content: this.originallyPublishedDate,
          scheme: 'DCTERMS.W3CDTF'
        },
        {
          name: 'DC.identifier',
          content: this.thisUrl,
          scheme: 'DCTERMS.URI'
        },
        {
          property: 'og:url',
          content: this.thisUrl
        },
      ],
      script: [
        {
          vmid: 'ldjson-schema',
          innerHTML: `{"@context": "http://schema.org","@type": "Dataset","@id": "${this.DOIlink}","name": "${this.datasetName}","publisher": "${this.organizationName}", "datePublished": "${this.datasetDetails.createdAt}", "dateModified": "${this.datasetDetails.updatedAt}", "Description": "${this.datasetDescription}"}`,
          type: 'application/ld+json'
        }
      ],
      __dangerouslyDisableSanitizersByTagID: {
        'ldjson-schema': ['innerHTML']
      }
    }
  }
}
</script>

<style lang="scss" scoped>
@import '../../assets/_spacing.scss';

.header {
  .gradient {
    padding: 1.5em 0;
    color: #f0f2f5;
    background-image: linear-gradient(90deg, #0026ff 0%, #00ffb9 100%);
  }
}

.dataset-details {
  background-color: #ffffff;
}

.copy-success-notification {
  color: #fff;
  margin-left: 5px
}

.fade-leave-active {
  transition: opacity .5s ease-out 2s;
}

.fade-enter {
  opacity: 1
}

.fade-leave-to {
  opacity: 0
}

.dataset-details {
  width: 100%;
  overflow-x: hidden;

  .dataset-info {
    background-color: #24245b;
    padding-bottom: 64px;
  }
}

// Footer styles
.dataset-info {
  h2 {
    color: #f9f2fc;
    font-size: 24px;
    font-weight: bold;
    line-height: 32px;
    margin: 56px 0 24px;
  }

  h3 {
    color: #f9f2fc;
    font-size: 16px;
    font-weight: 600;
    line-height: 16px;
    margin: 0 0 16px;
  }
}

.info-publishing-history {
  @media (min-width: 48em) {
    display: flex;
  }
  .info-text {
    margin-right: 90px;
  }
}

.info-text {
  color: #fff;
  font-size: 14px;
  line-height: 24px;

  a {
    color: #fff;
    text-decoration: underline;
  }

  .info-text-caps {
    text-transform: uppercase;
    color: #f2f6fc;
    font-size: 12px;
    font-weight: 600;
    line-height: 16px;
  }
}

.info-citation {
  border-radius: 4px;
  background-color: #f2f6fc;
  padding: 16px;
  color: #1c46bd;
  font-size: 14px;
  line-height: 24px;
  margin-bottom: 8px;
}

.info-citation-links {
  font-size: 14px;
  line-height: 16px;
  color: #c0c4cc;
  button, a {
    background: none;
    border: none;
    color: #c0c4cc;
    line-height: 16px;
    text-decoration: underline;
    font-size: 14px;
    cursor: pointer;
    padding: 0;
    margin-left: 11px;

    &.active {
      text-decoration: none;
      color: #fff;
    }
  }
}

// Markdown styles
.description-container {
  color: #000;
  font-size: 16px;
  line-height: 24px;
  padding-bottom: 92px;

  /deep/ {
    h1,
    p,
    h2,
    h3,
    blockquote,
    h4,
    pre {
      max-width: 616px;
    }

    h1,
    h2,
    h3,
    h4,
    h5 {
      margin: 0 0 8px;
    }

    h1 {
      font-size: 32px;
      font-weight: bold;
      line-height: 40px;
    }

    p {
      margin-bottom: 16px;
    }

    img {
      height: auto;
      max-width: 170%;
      margin-bottom: 20px;
      flex-basis: 50%;
      margin-top: 24px;
    }

    h2 {
      font-size: 24px;
      font-weight: bold;
      line-height: 32px;
    }

    h3 {
      font-size: 20px;
      font-weight: bold;
      line-height: 24px;
      letter-spacing: 0px;
    }

    h4 {
      font-size: 16px;
      font-weight: bold;
      line-height: 24px;
      text-transform: uppercase;
      letter-spacing: 0px;
    }

    ul {
      margin: 0 0 16px;
      padding: 0 0 0 18px;
    }

    blockquote {
      font-weight: normal;
      line-height: 24px;
      font-size: 16px;
      border-left: 8px solid #2760ff;
      margin-left: 0;

      p {
        margin-left: 16px;
      }
    }
    pre {
      background-color: #f1f1f3;
      line-height: 24px;
      padding: 16px;

      code {
        font-weight: normal;
        font-size: 14px;
      }
    }
  }
}
.files-table {
  margin: 24px 0 32px;
}
</style>
