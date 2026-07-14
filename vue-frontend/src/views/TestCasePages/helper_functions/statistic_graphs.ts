import type { ApexOptions } from "apexcharts";
import { computed } from "vue";
import type { Ref } from "vue";

export type FormatedData = {
    xdata: string[];
    xdate: string[];
    qa_models: string[];
    val_models: string[];
    aggregate: {
        answer_relevancy: {
            min: number | null;
            max: number | null;
            avg: number | null;
        } | null
        answer_correctness: {
            min: number | null;
            max: number | null;
            avg: number | null;
        } | null
        context_recall: {
            min: number | null;
            max: number | null;
            avg: number | null;
        } | null
        faithfulness: {
            min: number | null;
            max: number | null;
            avg: number | null;
        } | null
    } | null;
    answer_relevancy: number[];
    answer_correctness: number[];
    context_recall: number[];
    faithfulness: number[];
    answer_relevancy_categories: string[];
    answer_correctness_categories: string[];
    context_recall_categories: string[];
    faithfulness_categories: string[];
}


export const get_options_bar = function (formatedData: FormatedData) {


    return computed<ApexOptions>(() => ({
        chart: {
            type: 'bar',
            zoom: { enabled: false },
            toolbar: { show: true, tools: { download: true } }
        },
        plotOptions: {
            bar: {
                horizontal: false,
                columnWidth: '55%',
                borderRadius: 5,
                borderRadiusApplication: 'end',
            },
        },
        dataLabels: { enabled: false },
        stroke: {
            show: true,
            width: 2,
            colors: ['transparent'],
        },
        title: { text: 'Evaluation Progress', align: 'left' },
        xaxis: { categories: ["<0.25", "0.25-0.5", "0.5-0.7", "0.7-0.8", "0.8-0.9", ">0.9"] },
        yaxis: {
            title: {
                text: 'Count',
            },
        },
        fill: {
            opacity: 1,
        }
    }));

}



export const get_series_bar = function (formatedData: Ref<FormatedData>) {

    return computed(() => {
        const answer_categories = ["<0.25", "0.25-0.5", "0.5-0.7", "0.7-0.8", "0.8-0.9", ">0.9"]

        return [
            {
                name: 'Answer Relevancy', data: answer_categories.map((item) => {
                    return formatedData.value.answer_relevancy_categories.filter((category) => category == item).length
                })
            },
            {
                name: 'Answer Correctness', data: answer_categories.map((item) => {
                    return formatedData.value.answer_correctness_categories.filter((category) => category == item).length
                })
            },
            {
                name: 'Context Recall', data: answer_categories.map((item) => {
                    return formatedData.value.context_recall_categories.filter((category) => category == item).length
                })
            },
            {
                name: 'Faithfulness', data: answer_categories.map((item) => {
                    return formatedData.value.faithfulness_categories.filter((category) => category == item).length
                })
            },
        ]
    });
}
