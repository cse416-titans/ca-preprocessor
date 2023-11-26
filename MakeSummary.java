package com.cse416.titans.utils;

import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;
import java.util.ArrayList;
import java.util.List;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;
import org.springframework.stereotype.Service;

import com.cse416.titans.model.Cluster;
import com.cse416.titans.model.ClusterSet;
import com.cse416.titans.model.DistrictPlan;
import com.cse416.titans.model.Ensemble;
import com.cse416.titans.model.State;
import com.cse416.titans.service.ClusterService;
import com.cse416.titans.service.ClusterSetService;
import com.cse416.titans.service.DistrictPlanService;
import com.cse416.titans.service.EnsembleService;
import com.cse416.titans.service.StateService;

@Service
public class MakeSummary {
    public static void main(String[] args) throws IOException, ParseException {
        File folder = new File("C:\\Users\\ufg11\\Desktop\\ca-server\\src\\main\\java\\com\\cse416\\titans\\reseources");
        makeSummary(null, folder);
    }

    private static StateService stateService = new StateService(null);
    private static EnsembleService ensembleService = new EnsembleService(null);
    private static ClusterSetService clusterSetService = new ClusterSetService(null);
    private static ClusterService clusterService = new ClusterService(null);
    private static DistrictPlanService planService = new DistrictPlanService(null);

    // public MakeSummary (
    //     StateService stateService, 
    //     EnsembleService ensembleService,
    //     ClusterSetService clusterSetService,
    //     ClusterService clusterService,
    //     DistrictPlanService districtPlanService
    // ){
    //     this.stateService = stateService;
    //     this.ensembleService = ensembleService;
    //     this.clusterSetService = clusterSetService;
    //     this.clusterService = clusterService;
    //     this.planService = districtPlanService;
    // }

        public static void makeSummary(String root, File folder) throws IOException, ParseException {
        String name = folder.getName();
        List<String> list = new ArrayList<>();

        if (folder.isDirectory()) {
            for (File f : folder.listFiles()) {
                list.add(f.getName());
                makeSummary(name, f);
            }
        }

        // If it is json file, make it into an object and save it inside DB//
        else {
            JSONParser parser = new JSONParser();
            Reader reader = new FileReader(folder);
            JSONObject json = (JSONObject) parser.parse(reader);
            JSONArray features = (JSONArray) json.get("features");

            int republic = 0;
            int democrat = 0;

            for (Object feature : features) {
                JSONObject obj = (JSONObject) feature;
                double dem = (double) ((JSONObject) obj.get("properties")).get("Democratic");
                double rep = (double) ((JSONObject) obj.get("properties")).get("Republic");
                if (dem > rep) {
                    democrat++;
                }
                else {
                    republic++;
                }
            }


            // Create DistrictPlan Class to save in DB
            // TODO: Compute Opportunity Districts
            DistrictPlan plan = new DistrictPlan();
            plan.setClusterId(root);
            plan.setDemocrat(democrat);
            plan.setRepublic(republic);
            plan.setAvailability(true);
            plan.setGeoJson(json);
            plan.setId(name);
            plan.setName(name);

            // Need to be computed
            plan.setNumOfAAOpp(0);
            plan.setNumOfAsianOpp(0);
            plan.setNumOfHispanicOpp(0);
            plan.setNumOfWhiteOpp(0);

            // Add to DB
            planService.addPlan(plan);
        }

        // After went through everything in the folder
        // If this is Ensemble folder
        if (name.contains("Ensemble")) {
            // TODO
            List<ClusterSet> clusterSets = new ArrayList<ClusterSet>();
            int size = 0;
            for (String s : list) {
                ClusterSet clusterSet = clusterSetService.getClusterSetById(s);
                clusterSets.add(clusterSet);
                if (size == 0)
                size = clusterSet.getClusters().get(0).getPlans().size();
            }

            Ensemble ensemble = new Ensemble();
            ensemble.setId(name);
            ensemble.setName(name);
            ensemble.setStateId(root);
            ensemble.setClusterSets(clusterSets);
            ensemble.setSize(size);

            // Add to DB
            ensembleService.addEnsemble(ensemble);
        }

        // If this is ClusterSet folder
        else if (name.contains("Set")) {
            // TODO: Compute ClusterSeperationIndex, ClusterQualityIndex, and computeTime
            // How to know the distanceMeasureId?
            List<Cluster> clusters = new ArrayList<Cluster>();

            for (String s : list) {
                Cluster cluster = clusterService.getClusterById(s);
                clusters.add(cluster);
            }

            ClusterSet clusterSet = new ClusterSet();
            clusterSet.setId(name);
            clusterSet.setName(name);
            clusterSet.setEnsembleId(root);
            clusterSet.setClusters(clusters);

            // Need to Compute and Find
            clusterSet.setClusterQualityIndex(null);
            clusterSet.setClusterSeparationIndex(null);
            clusterSet.setComputeTime(null);
            clusterSet.setDistanceMeasureId(null);

            // Add to DB
            clusterSetService.addClusterSet(clusterSet);
        }

        // If this is Cluster folder
        else if (name.contains("Cluster")) {
            // TODO: Compute AvgClusterBoundary and DistanceBtwPlans
            List<DistrictPlan> plans = new ArrayList<DistrictPlan>();
            int totalDem = 0;
            int totalRep = 0;
            int totalAAOpp = 0;
            int totalAsianOpp = 0;
            int totalHispanicOpp = 0;
            int totalWhiteOpp = 0;
            
            for (String s : list) {
                DistrictPlan plan = planService.getPlanById(s);
                plans.add(plan);
                totalDem += plan.getDemocrat();
                totalRep += plan.getRepublic();
                totalAAOpp += plan.getNumOfAAOpp();
                totalAsianOpp += plan.getNumOfAsianOpp();
                totalHispanicOpp += plan.getNumOfHispanicOpp();
                totalWhiteOpp += plan.getNumOfWhiteOpp();
            }
            
            Cluster cluster = new Cluster();
            cluster.setId(name);
            cluster.setName(name);
            cluster.setClusterSetId(root);
            cluster.setPlans(plans);
            cluster.setNumOfPlans(list.size());
            cluster.setAvgDemocrat(Math.round(totalDem / list.size()));
            cluster.setAvgRepublic(Math.round(totalRep / list.size()));
            cluster.setAvgNumOfAAOpp(Math.round(totalAAOpp / list.size()));
            cluster.setAvgNumOfAsianOpp(Math.round(totalAsianOpp / list.size()));
            cluster.setAvgNumOfHispanicOpp(Math.round(totalHispanicOpp / list.size()));
            cluster.setAvgNumOfWhiteOpp(Math.round(totalWhiteOpp / list.size()));
            
            // Need to to be computed
            cluster.setAvgClusterBoundary(null);
            cluster.setDistBtwPlans(0);

            // Add to DB
            clusterService.addCluster(cluster);
        }
        // If this is State folder
        else {
            // TODO
            List<Ensemble> ensembles = new ArrayList<Ensemble>();
            for (String s : list) {
                Ensemble ensemble = ensembleService.getEnsembleById(s);
                ensembles.add(ensemble);
            }

            State state = new State();
            state.setId(name);
            state.setName(name);
            state.setEnsembles(ensembles);
            state.setCenter(null);
            state.setStatePlan(null);

            // Add to DB
            stateService.addState(state);
        }
    }
}
