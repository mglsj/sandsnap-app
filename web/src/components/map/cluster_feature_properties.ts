export interface ClusterProperties {
    cluster: true;
    cluster_id: number;
    point_count: number;
    total_size: number;
}

export interface SingleProperties {
    cluster?: false | undefined;
    id: number;
    image: string;
    createdAt: string;
    processedAt?: string;
    size?: number;
}

export type ClusterFeatureProperties = SingleProperties | ClusterProperties;