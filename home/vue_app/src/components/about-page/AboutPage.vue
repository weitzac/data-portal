<template>
    <div class="page">
        <el-row type="flex" justify="center">
            <el-col :xs="22" :sm="22" :md="16" :lg="12" :xl="12">
                <div class="about">
                    <h1>More than a data repository...</h1>
                    <p>The SPARC Portal provides interactive access to a growing collection of data, maps, and computational studies that focus on the role of the autonomic nervous system in controlling organ function. These resources are made available to the public with the intent of advancing bioelectronic medicine towards more precise treatment of diseases and conditions.</p>
                    <p>Launched in July 2019, the SPARC Portal currently hosts a growing set of digital resources generated by researchers funded through the <a href="https://sparc.science">NIH SPARC program</a>. We are continually adding new datasets, maps, and computational studies to the site — and are building new functionality to access and interact with those resources — so please check back periodically and sign up for our mailing list.</p>
                    <p>Data submission is currently limited to SPARC-funded investigators, but our long-term goal is to make this a resource to which the larger community can contribute. In the meantime, we’d love to hear any thoughts or suggestions you have for the Portal, so please reach out to share feedback.</p>
                    <hr>
                    <p class="subtext">Development of the SPARC Portal is a collaborative effort between groups based in the United States, Switzerland, and New Zealand. Collectively, these groups constitute SPARC’s Data & Resource Center. For more information about the NIH Common Fund SPARC program and the Data & Resource Center, please visit <a href="https://sparc.science">https://sparc.science.</a></p>
                    <div class="rule-container">
                        <div class="rule"></div>
                    </div>
                </div>
            </el-col>
        </el-row>
    </div>
</template>

<script>
    export default {
        name: 'about-page',
        components: {

        }
    }
</script>

<style scoped lang="scss">
    .page {
        padding-top: 8em;

        p {
            color: #606266;
        }
    }

    .about {
        text-align: center;
        min-height: 50vh;
    }

    .rule-container {
        padding-top: 3em;
        display: flex;
        justify-content: center;
        padding-bottom: 5em;
    }

    .rule {
        width: 5em;
        border-bottom: 5px solid #24245B;
    }

    .subtext {
        font-size: 12px
    }
</style>